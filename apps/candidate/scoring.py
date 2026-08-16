from dataclasses import dataclass, field
from typing import Optional

WEIGHTS = {
    "experience": 0.25,
    "education": 0.20,
    "skills": 0.15,
    "languages": 0.20,
    "immigration": 0.15,
    "documentation": 0.05,
}

EXPERIENCE_RELEVANCE = {"directly_related": 1.0, "partially_related": 0.8, "different": 0.5}
FIELD_ADJUSTMENT = {"related": 0, "partial": -20, "unrelated": -40}

EQF_TO_EDU_SCORE = {3: 20, 4: 40, 5: 55, 6: 70, 7: 90, 8: 100}

CEFR_SCORE = {None: 0, "": 0, "A1": 20, "A2": 40, "B1": 60, "B2": 80, "C1": 90, "C2": 100, "native": 100}
LOCAL_LANGUAGE_PENALTY = {"none": 0, "desirable": -10, "required": -30}

DIPLOMA_RECOGNITION_SCORE = {
    "recognized": 100, "in_progress": 80, "not_started": 50, "no_diploma": 0,
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


def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def _norm(s: str) -> str:
    return s.strip().lower()


@dataclass
class CandidateInput:
    years_experience: float = 0.0
    experience_relevance: str = "directly_related"
    eqf_level: int = 6
    field_relevance: str = "related"
    skills: set = field(default_factory=set)
    languages: dict = field(default_factory=dict)
    immigration_status: str = "other"
    work_authorization: str = ""
    diploma_recognition: str = "no_diploma"
    documents: dict = field(default_factory=dict)


@dataclass
class VacancyInput:
    required_skills: list = field(default_factory=list)
    required_language: Optional[str] = None
    required_language_level: Optional[str] = None
    local_language: str = "none"


def score_experience(c: CandidateInput):
    y = c.years_experience
    base = (0 if y <= 0 else 20 if y < 1 else 40 if y <= 2
            else 60 if y <= 5 else 80 if y <= 10 else 100)
    mult = EXPERIENCE_RELEVANCE.get(c.experience_relevance, 1.0)
    return _clamp(base * mult)


def score_education(c: CandidateInput):
    base = EQF_TO_EDU_SCORE.get(c.eqf_level, 0)
    adj = FIELD_ADJUSTMENT.get(c.field_relevance, 0)
    return _clamp(base + adj)


def score_skills(c: CandidateInput, v: VacancyInput):
    required = set(v.required_skills)
    if not required:
        return 100.0, [], []
    have = set(c.skills)
    matched = sorted(required & have)
    missing = sorted(required - have)
    return _clamp(len(matched) / len(required) * 100), matched, missing


def score_languages(c: CandidateInput, v: VacancyInput):
    if not v.required_language or not v.required_language_level:
        base = 100.0
    else:
        req = CEFR_SCORE.get(v.required_language_level, 0)
        cand = CEFR_SCORE.get(c.languages.get(v.required_language), 0)
        base = 100.0 if req == 0 else _clamp(cand / req * 100)
    base += LOCAL_LANGUAGE_PENALTY.get(v.local_language, 0)
    return _clamp(base)


def score_immigration(c: CandidateInput):
    s = c.immigration_status
    if s in ("eu_citizen", "dual_citizenship"):
        return 100.0
    if s == "permanent_resident":
        return 95.0
    if s == "no_legal_status":
        return 0.0
    wa = c.work_authorization
    if wa == "yes":
        return 90.0
    if wa == "in_progress":
        return 50.0
    if wa == "no":
        return 20.0
    return 20.0


def score_documentation(c: CandidateInput):
    diploma = DIPLOMA_RECOGNITION_SCORE.get(c.diploma_recognition, 0)
    points = min(100, sum(p for k, p in DOC_POINTS.items() if c.documents.get(k)))
    return _clamp(round(0.5 * diploma + 0.5 * points))


def classify(total: float) -> str:
    for threshold, label in CLASSIFICATION:
        if total >= threshold:
            return label
    return "Not Recommended"


def _weighted_total(blocks: dict) -> float:
    return round(sum(blocks[k] * WEIGHTS[k] for k in WEIGHTS), 2)


def score(c: CandidateInput, v: VacancyInput) -> dict:
    skills_score, matched, missing = score_skills(c, v)
    blocks = {
        "experience": round(score_experience(c), 2),
        "education": round(score_education(c), 2),
        "skills": round(skills_score, 2),
        "languages": round(score_languages(c, v), 2),
        "immigration": round(score_immigration(c), 2),
        "documentation": round(score_documentation(c), 2),
    }
    total = _weighted_total(blocks)
    return {
        "blocks": blocks,
        "weights": WEIGHTS,
        "total": total,
        "classification": classify(total),
        "matched_skills": matched,
        "missing_skills": missing,
        "evolution": _evolution(c, v, blocks, total),
    }


def _evolution(c: CandidateInput, v: VacancyInput, blocks: dict, current: float) -> dict:
    actions = []

    def gain(new_blocks):
        return round(_weighted_total({**blocks, **new_blocks}) - current, 2)

    _, _, missing = score_skills(c, v)
    if missing:
        g = gain({"skills": 100})
        if g > 0:
            actions.append({"gap_type": "skills",
                            "action": f"Acquire {len(missing)} missing skill(s)",
                            "detail": missing, "gain": g,
                            "context": {"missing_skills": missing}})

    if v.required_language and v.required_language_level:
        cur = c.languages.get(v.required_language)
        if CEFR_SCORE.get(cur, 0) < CEFR_SCORE.get(v.required_language_level, 0):
            c2 = CandidateInput(**{**c.__dict__,
                                   "languages": {**c.languages,
                                                 v.required_language: v.required_language_level}})
            g = gain({"languages": round(score_languages(c2, v), 2)})
            if g > 0:
                actions.append({"gap_type": "language",
                                "action": f"{v.required_language} -> {v.required_language_level}",
                                "gain": g,
                                "context": {"language": v.required_language,
                                            "current_level": cur or "None",
                                            "target_level": v.required_language_level}})

    if score_immigration(c) < 90 and c.immigration_status not in ("eu_citizen", "dual_citizenship"):
        c2 = CandidateInput(**{**c.__dict__, "work_authorization": "yes"})
        g = gain({"immigration": round(score_immigration(c2), 2)})
        if g > 0:
            actions.append({"gap_type": "immigration",
                            "action": "Complete work authorization / residency",
                            "gain": g, "context": {}})

    if c.diploma_recognition != "recognized":
        c2 = CandidateInput(**{**c.__dict__, "diploma_recognition": "recognized"})
        g = gain({"documentation": round(score_documentation(c2), 2)})
        if g > 0:
            actions.append({"gap_type": "degree_recognition",
                            "action": "Complete academic recognition",
                            "gain": g, "context": {}})

    potential = round(min(100.0, current + sum(a["gain"] for a in actions)), 2)
    return {"current": current, "potential": potential,
            "classification_potential": classify(potential), "actions": actions}