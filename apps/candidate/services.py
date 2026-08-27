from datetime import date
from apps.crosswalk.models import EscoOccupation, OccupationSkill, RomeEscoMapping
from . import scoring, recognition
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
    documents, recognition, eqf = {}, "dont_know", None
    if edu:
        eqf = edu.eqf_level
        recognition = RECOGNITION_MAP.get(edu.degree_recognized, "not_started")
        documents = {f: getattr(edu, f) for f in DOC_FIELDS}

    languages = {}
    for lng in profile.languages.all():
        # A certificate on file upgrades the evidence status from
        # declared/unverified to verified, and its CEFR level (when present)
        # takes precedence over the derived self-declared equivalent (spec §2).
        cert = lng.certificates.exclude(cefr_level="").order_by("-test_date").first()
        level = cert.cefr_level if cert else lng.level
        languages[lng.language] = {
            "level": level,
            "source": scoring.Evidence.VERIFIED if cert else scoring.Evidence.DECLARED_UNVERIFIED,
        }

    target = profile.target_country
    license_status = "dont_know"
    if target:
        cred = profile.practice_credentials.filter(country=target).first()
        if cred:
            license_status = cred.regulated_profession_status

    return scoring.CandidateInput(
        years_experience=profile.years_experience if profile.years_experience is not None else (
            _years(profile) if profile.experiences.exists() else None),
        experience_relevance=experience_relevance,
        eqf_level=eqf,
        field_relevance=field_relevance,
        has_education_record=edu is not None,
        skills={s.skill_uuid for s in profile.skills.all() if s.skill_uuid},
        verified_skills=set(),
        languages=languages,
        immigration_status=profile.immigration_status,
        work_authorization=profile.work_authorization,
        diploma_recognition=recognition,
        documents=documents,
        license_status=license_status,
        preferred_location=profile.preferred_location,
        willing_to_relocate=profile.willing_to_relocate,
        willing_to_change_country=profile.willing_to_change_country,
        preferred_work_model=profile.preferred_work_model,
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
        local_language=data.get("local_language", "none"),
        regulated=bool(getattr(occupation, "regulated", False)))
    result = scoring.score(c, v)
    _relabel_skills(result, essential_map)

    recognition_info = None
    target = profile.target_country
    if target is not None:
        recognition_info = recognition.determine_recognition_requirement(
            occupation, getattr(target, "country_code", None))
        # Keep the profile's PracticeCredential in sync with the
        # system-determined requirement (never overwrites the user's own
        # self-declared recognition/regulated_profession status fields).
        recognition.sync_practice_credential(profile, occupation, target)

    result["target"] = {
        "esco_uuid": str(occupation.esco_uuid), "code": occupation.code,
        "label": occupation_label(occupation, lang),
        "essential_skill_count": len(essential_map),
        "regulated": v.regulated,
        "recognition_requirement": recognition_info}
    return result


def _relabel_skills(result, skill_map):
    result["matched_skills"] = [skill_map.get(u, u) for u in result["matched_skills"]]
    result["missing_skills"] = [skill_map.get(u, u) for u in result["missing_skills"]]
    jm = result.get("job_match_score", {})
    jm["matched_skills"] = result["matched_skills"]
    jm["missing_skills"] = result["missing_skills"]
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


# ---------------------------------------------------------------------------
# Final Review support (client feedback: user must be able to review and
# correct information before completing the assessment, with Privacy
# Notice/Terms shown separately from optional consents such as marketing).
# This is backend support for that screen - no frontend was provided in
# this delivery, so the frontend team renders the UI from this payload.
# ---------------------------------------------------------------------------

def _field_status(value) -> str:
    if value in (None, "", [], {}):
        return "missing"
    return "declared"


def review_summary(profile) -> dict:
    """A section-by-section, field-by-field readiness summary the frontend
    can render as the pre-submission review screen. Every value shown is
    exactly what the user entered (self-declared) - nothing here is
    computed or inferred."""
    sections = [
        {"section": "identity_account", "label": "Identity & account (optional here)", "fields": [
            {"field": "full_name", "value": profile.full_name, "status": _field_status(profile.full_name)},
            {"field": "email", "value": profile.email, "status": _field_status(profile.email)},
            {"field": "phone_number", "value": profile.phone_number, "status": _field_status(profile.phone_number)},
            {"field": "linkedin_profile", "value": profile.linkedin_profile, "status": _field_status(profile.linkedin_profile)},
            {"field": "age", "value": profile.age, "status": _field_status(profile.age)},
        ]},
        {"section": "location_immigration", "label": "Location & work authorization", "fields": [
            {"field": "target_country", "value": str(profile.target_country) if profile.target_country else None,
             "status": _field_status(profile.target_country)},
            {"field": "work_authorization", "value": profile.work_authorization,
             "status": _field_status(profile.work_authorization)},
        ]},
        {"section": "education", "label": "Education & recognition", "fields": [
            {"field": f"education[{i}].eqf_level", "value": e.eqf_level, "status": "declared"}
            for i, e in enumerate(profile.education.all())
        ] or [{"field": "education", "value": None, "status": "missing"}]},
        {"section": "experience", "label": "Professional experience", "fields": [
            {"field": "years_experience", "value": profile.years_experience,
             "status": _field_status(profile.years_experience)},
        ]},
        {"section": "languages", "label": "Languages", "fields": [
            {"field": f"languages[{i}].{lng.language}", "value": lng.level,
             "status": "verified" if lng.certificates.exists() else "declared"}
            for i, lng in enumerate(profile.languages.all())
        ] or [{"field": "languages", "value": None, "status": "missing"}]},
        {"section": "skills", "label": "Skills", "fields": [
            {"field": "skills_count", "value": profile.skills.count(),
             "status": "declared" if profile.skills.exists() else "missing"},
        ]},
        {"section": "flexibility", "label": "Flexibility & preferences", "fields": [
            {"field": "willing_to_change_occupation", "value": profile.willing_to_change_occupation,
             "status": _field_status(profile.willing_to_change_occupation)},
            {"field": "preferred_location", "value": profile.preferred_location,
             "status": _field_status(profile.preferred_location)},
            {"field": "expected_salary_min/max", "value": [profile.expected_salary_min, profile.expected_salary_max],
             "status": "declared" if profile.expected_salary_min or profile.expected_salary_max else "missing"},
        ]},
        {"section": "consent", "label": "Consent (kept separate, per GDPR/data-minimisation rules)", "fields": [
            {"field": "privacy_notice_terms_accepted", "value": profile.consent_given, "status": "declared"},
            {"field": "marketing_consent", "value": profile.marketing_consent, "status": "declared"},
        ]},
    ]
    all_fields = [f for s in sections for f in s["fields"]]
    missing_count = sum(1 for f in all_fields if f["status"] == "missing")
    return {
        "sections": sections,
        "ready_for_submission": True,  # nothing here is mandatory except target_country for matching
        "declared_field_count": len(all_fields) - missing_count,
        "missing_field_count": missing_count,
    }