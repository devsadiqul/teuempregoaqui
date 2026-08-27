"""
Recommendation scoring engine.

Implements the methodology validated with the client (Fernando Thompson,
OpenDoor Integration Technologies) on 2026-08-19:

1. ESCO + job-specific scoring stay separate and auditable — every
   sub-score is returned individually, never folded into a single opaque
   number.
2. "No Evidence, No Points, No Inference" — if information is missing or
   unverifiable, the corresponding component scores 0 and is labelled
   ``missing`` / ``declared_unverified`` / ``not_compliant``. A 0 never
   means "the candidate lacks this"; it means "the system has no
   sufficient evidence to award points."
3. Missing evidence is turned into an actionable recommendation (see
   ``resolutions.py`` for the human-readable card).
4. Mandatory eligibility requirements (e.g. a legally required
   professional licence) are evaluated separately from ranking factors.
   A candidate who fails a mandatory requirement is flagged
   "not currently eligible" — this does not silently reduce the score.
5. Two distinct indicators are produced:
     A. Job Match Score           — fit against one specific vacancy.
     B. European Employability Index — general readiness for the EU
        labour market, independent of any single vacancy.
6. Recognition-related requirements (apostille, professional
   registration, diploma recognition) only affect the score when the
   target occupation/country actually requires them (``VacancyInput.regulated``).
   They are never applied as a blanket penalty.
7. A Confidence Score accompanies each indicator: the proportion of its
   applicable, weighted dimensions that are NOT ``missing`` evidence -
   i.e. how much of the number is backed by some evidence (verified or
   declared) versus how much is a 0 standing in for an unanswered field.

See docs/Recommendation_Scoring_Specification.docx for the full
methodology document shared with the client.
"""

from dataclasses import dataclass, field
from typing import Optional


class Evidence:
    """Provenance/verification status of a data point. See spec section 2."""
    VERIFIED = "verified"                     # supported by adequate evidence
    DECLARED_UNVERIFIED = "declared_unverified"  # user-provided, not yet verified
    MISSING = "missing"                       # no information/evidence available
    NOT_COMPLIANT = "not_compliant"            # evidence confirms requirement is NOT met
    NOT_APPLICABLE = "not_applicable"          # dimension irrelevant for this vacancy/country


WEIGHTS_JOB_MATCH = {
    "esco_occupational_match": 0.20,
    "skills": 0.20,
    "experience": 0.15,
    "languages": 0.20,
    "location": 0.15,
    "recognition": 0.10,  # only applied when VacancyInput.regulated is True
}

WEIGHTS_EMPLOYABILITY = {
    "education": 0.20,
    "skills": 0.15,
    "experience": 0.20,
    "languages": 0.20,
    "immigration_readiness": 0.15,
    "documentation_readiness": 0.10,
}

EXPERIENCE_RELEVANCE = {"directly_related": 1.0, "partially_related": 0.8, "different": 0.5}
FIELD_ADJUSTMENT = {"related": 0, "partial": -20, "unrelated": -40}

EQF_TO_EDU_SCORE = {3: 20, 4: 40, 5: 55, 6: 70, 7: 90, 8: 100}

CEFR_SCORE = {None: 0, "": 0, "A1": 20, "A2": 40, "B1": 60, "B2": 80, "C1": 90, "C2": 100, "native": 100}
LOCAL_LANGUAGE_PENALTY = {"none": 0, "desirable": -10, "required": -30}

DIPLOMA_RECOGNITION_SCORE = {
    "recognized": 100, "in_progress": 80, "not_started": 50,
    "no_diploma": 0, "dont_know": 0,
}
DOC_POINTS = {
    "physical_diploma": 15, "academic_transcript": 15, "course_syllabi": 15,
    "apostille_completed": 15, "certified_translation": 15,
    "grades_converted_eu_scale": 15, "recognition_process_started": 10,
}

CLASSIFICATION = [
    (90, "Excellent Compatibility"), (80, "Good Compatibility"),
    (70, "Moderate Compatibility"), (60, "Partial Compatibility"),
    (50, "Low Compatibility"), (0, "Not Recommended"),
]

NOT_ELIGIBLE_REASON = "Not currently eligible - mandatory requirement not met."


def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


@dataclass
class CandidateInput:
    years_experience: Optional[float] = None
    experience_relevance: str = "directly_related"
    eqf_level: Optional[int] = None
    field_relevance: str = "related"
    skills: set = field(default_factory=set)
    verified_skills: set = field(default_factory=set)
    # languages: {lang: {"level": "B2", "source": Evidence.DECLARED_UNVERIFIED|VERIFIED}}
    languages: dict = field(default_factory=dict)
    immigration_status: str = "other"
    work_authorization: str = ""  # yes | no | pending | dont_know (self-declared)
    diploma_recognition: str = "dont_know"
    has_education_record: bool = False
    documents: dict = field(default_factory=dict)
    license_status: str = "dont_know"  # yes | no | in_progress | dont_know
    preferred_location: str = ""  # free text, e.g. "Lisboa" or "Paris (75)"
    willing_to_relocate: bool = False       # within the target country
    willing_to_change_country: bool = False  # across countries
    preferred_work_model: str = "no_preference"  # on_site | hybrid | remote | no_preference


@dataclass
class VacancyInput:
    required_skills: list = field(default_factory=list)
    required_language: Optional[str] = None
    required_language_level: Optional[str] = None
    local_language: str = "none"
    regulated: bool = False  # target occupation/country requires professional recognition/licence
    location: Optional[str] = None    # free-text vacancy location, e.g. "Paris (75)"
    remote_allowed: bool = False


def _sub(value, weight, status, note=""):
    return {"score": round(_clamp(value), 2), "weight": weight, "status": status, "note": note}


# ---------------------------------------------------------------------------
# Eligibility (mandatory requirement) — evaluated BEFORE ranking, per spec §4
# ---------------------------------------------------------------------------

def check_eligibility(c: CandidateInput, v: VacancyInput) -> dict:
    if v.regulated and c.license_status != "yes":
        return {"eligible": False, "reason": NOT_ELIGIBLE_REASON,
                "requirement": "professional_licence_or_registration",
                "evidence_status": (Evidence.NOT_COMPLIANT if c.license_status == "no"
                                     else Evidence.MISSING if c.license_status == "dont_know"
                                     else Evidence.DECLARED_UNVERIFIED)}
    return {"eligible": True, "reason": None, "requirement": None, "evidence_status": None}


# ---------------------------------------------------------------------------
# Individual dimension scorers — each returns (value, status, note)
# ---------------------------------------------------------------------------

def score_experience(c: CandidateInput):
    if c.years_experience is None:
        return 0.0, Evidence.MISSING, "Years of experience not provided."
    y = c.years_experience
    base = (0 if y <= 0 else 20 if y < 1 else 40 if y <= 2
            else 60 if y <= 5 else 80 if y <= 10 else 100)
    mult = EXPERIENCE_RELEVANCE.get(c.experience_relevance, 1.0)
    return _clamp(base * mult), Evidence.DECLARED_UNVERIFIED, "Self-declared work history."


def score_education(c: CandidateInput):
    if not c.has_education_record or c.eqf_level is None:
        return 0.0, Evidence.MISSING, "No education record on file."
    base = EQF_TO_EDU_SCORE.get(c.eqf_level, 0)
    adj = FIELD_ADJUSTMENT.get(c.field_relevance, 0)
    return _clamp(base + adj), Evidence.DECLARED_UNVERIFIED, "Self-declared qualification."


def score_esco_occupational_match(c: CandidateInput):
    """Proxy for ESCO occupational compatibility: field relevance to the
    target occupation. Kept separate from the raw skills-set overlap."""
    if not c.has_education_record and c.years_experience is None:
        return 0.0, Evidence.MISSING, "Insufficient profile data to assess occupational fit."
    base = 100 + FIELD_ADJUSTMENT.get(c.field_relevance, 0)
    return _clamp(base), Evidence.DECLARED_UNVERIFIED, "Derived from self-declared field/experience relevance."


def score_skills(c: CandidateInput, v: VacancyInput):
    required = set(v.required_skills)
    if not required:
        return 100.0, Evidence.NOT_APPLICABLE, [], [], "Vacancy defines no essential skills."
    have = set(c.skills)
    matched = sorted(required & have)
    missing = sorted(required - have)
    status = (Evidence.VERIFIED if required & c.verified_skills == required and required
              else Evidence.DECLARED_UNVERIFIED if have else Evidence.MISSING)
    value = 0.0 if not required else _clamp(len(matched) / len(required) * 100)
    return value, status, matched, missing, "Skill match against ESCO essential skills."


def score_languages(c: CandidateInput, v: VacancyInput):
    if not v.required_language or not v.required_language_level:
        return 100.0, Evidence.NOT_APPLICABLE, "No language requirement for this vacancy."
    entry = c.languages.get(v.required_language)
    if not entry:
        return 0.0, Evidence.MISSING, f"No declared proficiency in {v.required_language}."
    req = CEFR_SCORE.get(v.required_language_level, 0)
    cand = CEFR_SCORE.get(entry.get("level"), 0)
    base = 100.0 if req == 0 else _clamp(cand / req * 100)
    base += LOCAL_LANGUAGE_PENALTY.get(v.local_language, 0)
    status = entry.get("source", Evidence.DECLARED_UNVERIFIED)
    return _clamp(base), status, "Self-declared unless a certificate is on file."


def score_immigration(c: CandidateInput):
    s = c.immigration_status
    if s in ("eu_citizen", "dual_citizenship"):
        return 100.0, Evidence.DECLARED_UNVERIFIED, ""
    if s == "permanent_resident":
        return 95.0, Evidence.DECLARED_UNVERIFIED, ""
    wa = c.work_authorization
    if wa == "yes":
        return 90.0, Evidence.DECLARED_UNVERIFIED, "Self-declared work authorization."
    if wa == "pending":
        return 50.0, Evidence.DECLARED_UNVERIFIED, "Authorization pending."
    if wa == "no":
        return 10.0, Evidence.NOT_COMPLIANT, "Declared as not currently authorized."
    return 0.0, Evidence.MISSING, "Work authorization status not declared."


def score_documentation(c: CandidateInput):
    if c.diploma_recognition == "dont_know" and not c.documents:
        return 0.0, Evidence.MISSING, "No recognition status or supporting documents declared."
    diploma = DIPLOMA_RECOGNITION_SCORE.get(c.diploma_recognition, 0)
    points = min(100, sum(p for k, p in DOC_POINTS.items() if c.documents.get(k)))
    status = (Evidence.VERIFIED if c.diploma_recognition == "recognized"
              else Evidence.NOT_COMPLIANT if c.diploma_recognition == "no_diploma"
              else Evidence.DECLARED_UNVERIFIED)
    return _clamp(round(0.5 * diploma + 0.5 * points)), status, "Recognition status is self-declared unless verified."


def score_location(c: CandidateInput, v: VacancyInput):
    """Geographic/work-preference compatibility. Vacancy location is a
    free-text field (e.g. from France Travail offers, "Paris (75)"), so
    matching is a conservative substring check rather than true geocoding -
    this is stated explicitly in the note so the score is never overread."""
    if not v.location:
        return 100.0, Evidence.NOT_APPLICABLE, "Vacancy has no location constraint (e.g. fully remote or unspecified)."

    if c.preferred_work_model == "remote" and v.remote_allowed:
        return 100.0, Evidence.DECLARED_UNVERIFIED, "Remote work preference matches a remote-eligible vacancy."

    if not c.preferred_location and not c.willing_to_relocate and not c.willing_to_change_country:
        return 0.0, Evidence.MISSING, "No location preference or relocation willingness declared."

    if c.preferred_location and c.preferred_location.strip().lower() in v.location.strip().lower():
        return 100.0, Evidence.DECLARED_UNVERIFIED, "Preferred location matches the vacancy location (text match)."

    if c.willing_to_relocate or c.willing_to_change_country:
        return 65.0, Evidence.DECLARED_UNVERIFIED, "Preferred location differs, but candidate declared willingness to relocate."

    return 25.0, Evidence.DECLARED_UNVERIFIED, "Preferred location differs from the vacancy location; no relocation willingness declared."


def classify(total: float) -> str:
    for threshold, label in CLASSIFICATION:
        if total >= threshold:
            return label
    return "Not Recommended"


def _weighted_total(dims: dict, weights: dict) -> float:
    applicable = {k: w for k, w in weights.items()
                  if dims.get(k, {}).get("status") != Evidence.NOT_APPLICABLE}
    wsum = sum(applicable.values()) or 1.0
    return round(sum(dims[k]["score"] * (applicable[k] / wsum) for k in applicable), 2)


def _confidence(dims: dict, weights: dict) -> float:
    """Share of the weighted total that is backed by SOME evidence
    (verified or declared) rather than standing in for a 0 on a Missing
    field. Not-applicable dimensions are excluded from the base, exactly
    as in _weighted_total, so the two numbers are directly comparable."""
    applicable = {k: w for k, w in weights.items()
                  if dims.get(k, {}).get("status") != Evidence.NOT_APPLICABLE}
    wsum = sum(applicable.values()) or 1.0
    covered = sum(applicable[k] for k in applicable if dims[k]["status"] != Evidence.MISSING)
    return round(covered / wsum * 100, 2)


# ---------------------------------------------------------------------------
# A. Job Match Score — fit against one specific vacancy
# ---------------------------------------------------------------------------

def job_match_score(c: CandidateInput, v: VacancyInput) -> dict:
    eligibility = check_eligibility(c, v)

    esco_v, esco_s, esco_n = score_esco_occupational_match(c)
    skills_v, skills_s, matched, missing, skills_n = score_skills(c, v)
    exp_v, exp_s, exp_n = score_experience(c)
    lang_v, lang_s, lang_n = score_languages(c, v)
    loc_v, loc_s, loc_n = score_location(c, v)

    dims = {
        "esco_occupational_match": _sub(esco_v, WEIGHTS_JOB_MATCH["esco_occupational_match"], esco_s, esco_n),
        "skills": _sub(skills_v, WEIGHTS_JOB_MATCH["skills"], skills_s, skills_n),
        "experience": _sub(exp_v, WEIGHTS_JOB_MATCH["experience"], exp_s, exp_n),
        "languages": _sub(lang_v, WEIGHTS_JOB_MATCH["languages"], lang_s, lang_n),
        "location": _sub(loc_v, WEIGHTS_JOB_MATCH["location"], loc_s, loc_n),
    }

    if v.regulated:
        doc_v, doc_s, doc_n = score_documentation(c)
        dims["recognition"] = _sub(doc_v, WEIGHTS_JOB_MATCH["recognition"], doc_s, doc_n)
    else:
        dims["recognition"] = _sub(0, WEIGHTS_JOB_MATCH["recognition"], Evidence.NOT_APPLICABLE,
                                    "Recognition not required for this occupation/country.")

    total = _weighted_total(dims, WEIGHTS_JOB_MATCH)
    confidence = _confidence(dims, WEIGHTS_JOB_MATCH)

    return {
        "total": total,
        "confidence": confidence,
        "classification": classify(total) if eligibility["eligible"] else "Not Currently Eligible",
        "eligibility": eligibility,
        "dimensions": dims,
        "matched_skills": matched,
        "missing_skills": missing,
    }


# ---------------------------------------------------------------------------
# B. European Employability Index — general readiness, not vacancy-specific
# ---------------------------------------------------------------------------

def european_employability_index(c: CandidateInput) -> dict:
    edu_v, edu_s, edu_n = score_education(c)
    exp_v, exp_s, exp_n = score_experience(c)
    imm_v, imm_s, imm_n = score_immigration(c)
    doc_v, doc_s, doc_n = score_documentation(c)

    best_lang = max((CEFR_SCORE.get(e.get("level"), 0) for e in c.languages.values()), default=None)
    if best_lang is None:
        lang_v, lang_s, lang_n = 0.0, Evidence.MISSING, "No languages declared."
    else:
        lang_v, lang_s, lang_n = float(best_lang), Evidence.DECLARED_UNVERIFIED, "Best self-declared language level."

    skills_v = 100.0 if c.skills else 0.0
    skills_s = Evidence.DECLARED_UNVERIFIED if c.skills else Evidence.MISSING
    skills_n = "" if c.skills else "No skills declared."

    dims = {
        "education": _sub(edu_v, WEIGHTS_EMPLOYABILITY["education"], edu_s, edu_n),
        "skills": _sub(skills_v, WEIGHTS_EMPLOYABILITY["skills"], skills_s, skills_n),
        "experience": _sub(exp_v, WEIGHTS_EMPLOYABILITY["experience"], exp_s, exp_n),
        "languages": _sub(lang_v, WEIGHTS_EMPLOYABILITY["languages"], lang_s, lang_n),
        "immigration_readiness": _sub(imm_v, WEIGHTS_EMPLOYABILITY["immigration_readiness"], imm_s, imm_n),
        "documentation_readiness": _sub(doc_v, WEIGHTS_EMPLOYABILITY["documentation_readiness"], doc_s, doc_n),
    }
    total = _weighted_total(dims, WEIGHTS_EMPLOYABILITY)
    confidence = _confidence(dims, WEIGHTS_EMPLOYABILITY)
    return {"total": total, "confidence": confidence, "classification": classify(total), "dimensions": dims}


# ---------------------------------------------------------------------------
# Actionable recommendations from evidence gaps (spec §3)
# ---------------------------------------------------------------------------

def _evolution(c: CandidateInput, v: VacancyInput, jm: dict) -> dict:
    actions = []
    current = jm["total"]

    def with_dim(name, new_value):
        dims = {k: dict(d) for k, d in jm["dimensions"].items()}
        dims[name]["score"] = new_value
        return _weighted_total(dims, WEIGHTS_JOB_MATCH)

    if jm["missing_skills"]:
        g = round(with_dim("skills", 100) - current, 2)
        if g > 0:
            actions.append({"gap_type": "skills",
                            "action": f"Acquire {len(jm['missing_skills'])} missing skill(s)",
                            "detail": jm["missing_skills"], "gain": g,
                            "evidence_status": jm["dimensions"]["skills"]["status"],
                            "context": {"missing_skills": jm["missing_skills"]}})

    lang_dim = jm["dimensions"]["languages"]
    if lang_dim["status"] in (Evidence.MISSING, Evidence.DECLARED_UNVERIFIED) and v.required_language:
        if lang_dim["score"] < 100:
            g = round(with_dim("languages", 100) - current, 2)
            if g > 0:
                actions.append({"gap_type": "language",
                                "action": f"{v.required_language} -> {v.required_language_level}",
                                "gain": g, "evidence_status": lang_dim["status"],
                                "context": {"language": v.required_language,
                                            "current_level": (c.languages.get(v.required_language) or {}).get("level") or "None",
                                            "target_level": v.required_language_level}})

    loc_dim = jm["dimensions"]["location"]
    if loc_dim["status"] != Evidence.NOT_APPLICABLE and loc_dim["score"] < 100:
        g = round(with_dim("location", 100) - current, 2)
        if g > 0:
            actions.append({"gap_type": "location",
                            "action": "Declare a location preference or relocation willingness",
                            "gain": g, "evidence_status": loc_dim["status"],
                            "context": {"vacancy_location": v.location}})

    if not jm["eligibility"]["eligible"]:
        actions.append({"gap_type": "mandatory_requirement",
                        "action": "Obtain the required professional licence/registration",
                        "gain": 0.0, "evidence_status": jm["eligibility"]["evidence_status"],
                        "context": {"requirement": jm["eligibility"]["requirement"]}})
    elif v.regulated and jm["dimensions"]["recognition"]["status"] != Evidence.VERIFIED:
        g = round(with_dim("recognition", 100) - current, 2)
        if g > 0:
            actions.append({"gap_type": "degree_recognition",
                            "action": "Complete academic/professional recognition",
                            "gain": g, "evidence_status": jm["dimensions"]["recognition"]["status"],
                            "context": {}})

    potential = round(min(100.0, current + sum(a["gain"] for a in actions)), 2)
    return {"current": current, "potential": potential,
            "classification_potential": classify(potential), "actions": actions}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def score(c: CandidateInput, v: VacancyInput) -> dict:
    """Backward/forward-compatible entry point used by services.run_match().

    Returns both indicators plus the legacy-shaped fields (``blocks``,
    ``total``, ``classification``, ``matched_skills``, ``missing_skills``,
    ``evolution``) so existing serializers/consumers keep working while the
    frontend migrates to the new ``job_match_score`` / ``employability_index``
    structure.
    """
    jm = job_match_score(c, v)
    eei = european_employability_index(c)
    evolution = _evolution(c, v, jm)

    return {
        "job_match_score": jm,
        "employability_index": eei,
        # legacy-compatible mirror (deprecated - use job_match_score instead)
        "blocks": {k: d["score"] for k, d in jm["dimensions"].items()},
        "total": jm["total"],
        "classification": jm["classification"],
        "matched_skills": jm["matched_skills"],
        "missing_skills": jm["missing_skills"],
        "evolution": evolution,
    }