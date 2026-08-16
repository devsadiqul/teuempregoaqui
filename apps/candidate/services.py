from datetime import date
from apps.crosswalk.models import EscoOccupation, OccupationSkill, RomeEscoMapping
from . import scoring
from .models import CandidateProfile

RECOGNITION_MAP = {
    "yes": "recognized", "in_progress": "in_progress",
    "no": "not_started", "dont_know": "not_started",
}
DOC_FIELDS = [
    "physical_diploma", "academic_transcript", "course_syllabi",
    "apostille_completed", "certified_translation",
    "grades_converted_eu_scale", "recognition_process_started",
]


def session_key(request) -> str:
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _auth_user_id(request):
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return str(user.id)
    return None


def visible_profiles(request):
    qs = CandidateProfile.objects.prefetch_related(
        "education", "experiences", "languages", "certifications", "skills")
    sk = session_key(request)
    uid = _auth_user_id(request)
    if uid:
        return (qs.filter(user_id=uid) |
                qs.filter(mode=CandidateProfile.Mode.PRIVATE, session_key=sk)).distinct()
    return qs.filter(mode=CandidateProfile.Mode.PRIVATE, session_key=sk)


def get_visible_profile(request, pk):
    profile = visible_profiles(request).filter(pk=pk).first()
    if profile is None or profile.is_expired:
        return None
    return profile


def resolve_occupation(esco_uuid=None, rome_appellation_id=None):
    if esco_uuid:
        return EscoOccupation.objects.filter(pk=esco_uuid).first()
    if rome_appellation_id:
        m = (RomeEscoMapping.objects.filter(rome_appellation_id=rome_appellation_id)
             .select_related("occupation").first())
        return m.occupation if m else None
    return None


def essential_skill_map(occupation, lang="en"):
    skill_map = {str(u): l for u, l in OccupationSkill.objects.filter(
        occupation=occupation, relation=OccupationSkill.ESSENTIAL
    ).values_list("skill_uuid", "skill_label")}
    if lang in ("es", "pt") and skill_map:
        from apps.crosswalk.i18n import skill_label_map
        loc = skill_label_map(skill_map.keys(), lang)
        skill_map = {u: loc.get(u, l) for u, l in skill_map.items()}
    return skill_map


def occupation_label(occupation, lang="en"):
    fn = getattr(occupation, "localized_label", None)
    return fn(lang) if fn else occupation.label


def candidate_input_from_profile(profile, *, experience_relevance, field_relevance):
    edu = profile.education.order_by("-eqf_level").first()
    documents, recognition, eqf = {}, "no_diploma", 6
    if edu:
        eqf = edu.eqf_level
        recognition = RECOGNITION_MAP.get(edu.degree_recognized, "not_started")
        documents = {f: getattr(edu, f) for f in DOC_FIELDS}
    return scoring.CandidateInput(
        years_experience=_years(profile),
        experience_relevance=experience_relevance,
        eqf_level=eqf,
        field_relevance=field_relevance,
        skills={s.skill_uuid for s in profile.skills.all() if s.skill_uuid},
        languages={lng.language: lng.level for lng in profile.languages.all()},
        immigration_status=profile.immigration_status,
        work_authorization=profile.work_authorization,
        diploma_recognition=recognition,
        documents=documents,
    )


def run_match(profile, occupation, data, lang="en"):
    essential_map = essential_skill_map(occupation, lang)
    c = candidate_input_from_profile(
        profile,
        experience_relevance=data.get("experience_relevance", "directly_related"),
        field_relevance=data.get("field_relevance", "related"))
    v = scoring.VacancyInput(
        required_skills=list(essential_map.keys()),
        required_language=data.get("required_language"),
        required_language_level=data.get("required_language_level"),
        local_language=data.get("local_language", "none"))
    result = scoring.score(c, v)
    _relabel_skills(result, essential_map)
    result["target"] = {
        "esco_uuid": str(occupation.esco_uuid), "code": occupation.code,
        "label": occupation_label(occupation, lang),
        "essential_skill_count": len(essential_map)}
    return result


def _relabel_skills(result, skill_map):
    result["matched_skills"] = [skill_map.get(u, u) for u in result["matched_skills"]]
    result["missing_skills"] = [skill_map.get(u, u) for u in result["missing_skills"]]
    for action in result.get("evolution", {}).get("actions", []):
        if action.get("gap_type") == "skills":
            action["detail"] = [skill_map.get(u, u) for u in action["detail"]]
            if "missing_skills" in action.get("context", {}):
                action["context"]["missing_skills"] = [
                    skill_map.get(u, u) for u in action["context"]["missing_skills"]]


def _years(profile):
    if profile.years_experience is not None:
        return float(profile.years_experience)
    total_days, today = 0, date.today()
    for e in profile.experiences.all():
        if e.start_date:
            total_days += ((e.end_date or today) - e.start_date).days
    return round(total_days / 365.25, 1)