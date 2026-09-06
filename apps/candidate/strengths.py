"""
Candidate-facing "Strengths & Weaknesses" summary.

``job_match_score`` and ``employability_index`` (see scoring.py) are
built to be auditable: every dimension carries a raw score, a weight and
a technical evidence status/note. That is the right shape for the
system and for support staff, but it is not friendly reading for the
candidate themselves.

This module does not change or re-derive any score. It only re-reads
the existing dimensions and, for every single one, tells the candidate
in plain language:
  1. whether it currently helps ("strength"), partly helps
     ("developing") or hurts ("weakness") their result, and why
     (``explanation``);
  2. exactly how many points their overall score would move if THIS
     dimension alone reached its maximum, all else being equal
     (``current_overall_score`` -> ``potential_overall_score``,
     ``points_gain``) - e.g. "you're at 30, fixing this alone gets you
     to 40"; and
  3. concretely what to do about it (``how_to_improve``) - never just
     the problem on its own.

Nothing here changes an existing score, weight or status; it is a
read-only, additive explanation layer on top of them.
"""

from apps.candidate.scoring import Evidence
from apps.candidate.strengths_text import (
    DIMENSION_LABELS, EXPLANATIONS, ACTIONS, SUMMARY_TEXT,
    TOP_OPPORTUNITY_TEXT, SCORE_GROUP_LABELS,
)

STRONG_THRESHOLD = 70
WEAK_THRESHOLD = 50
WEAK_STATUSES = (Evidence.MISSING, Evidence.NOT_COMPLIANT)

_VALID_LANGS = ("en", "es", "pt")


def _lang(lang):
    return lang if lang in _VALID_LANGS else "en"


def _classify(score, status):
    if status in WEAK_STATUSES or score < WEAK_THRESHOLD:
        return "weakness"
    if score >= STRONG_THRESHOLD:
        return "strength"
    return "developing"


def _label(dim_name, lang):
    labels = DIMENSION_LABELS.get(dim_name, {})
    return labels.get(lang) or labels.get("en") or dim_name.replace("_", " ").title()


def _render(source: dict, template_key, classification, lang, ctx) -> str:
    templates = source.get(template_key, {}).get(classification, {})
    template = templates.get(lang) or templates.get("en")
    if not template:
        return ""
    try:
        return template.format(**ctx)
    except (KeyError, IndexError):
        return template


def _weighted_total(dims: dict) -> float:
    """Same formula as scoring._weighted_total, kept local so this module
    never has to reach into scoring's private helpers or its weight
    constants - it derives everything from the ``weight`` already stored
    on each dimension by scoring.py."""
    applicable = {k: d["weight"] for k, d in dims.items() if d["status"] != Evidence.NOT_APPLICABLE}
    wsum = sum(applicable.values()) or 1.0
    return round(sum(dims[k]["score"] * (applicable[k] / wsum) for k in applicable), 2)


def _potential_if_full(dims: dict, dim_name: str, target: float = 100.0) -> float:
    """What the overall total would become if ONLY ``dim_name`` reached
    ``target``, every other dimension held exactly as-is."""
    if dim_name not in dims or dims[dim_name]["status"] == Evidence.NOT_APPLICABLE:
        return _weighted_total(dims)
    patched = {k: dict(d) for k, d in dims.items()}
    patched[dim_name]["score"] = target
    return _weighted_total(patched)


def _build_group(dims: dict, current_total: float, lang: str, extra_ctx: dict,
                  template_key_map: dict = None) -> dict:
    """``template_key_map`` lets a dimension borrow another dimension's
    copy templates (e.g. employability's generic "skills"/"languages"
    dimensions read differently from job_match_score's job-specific
    ones) while keeping the reported ``dimension`` name unchanged."""
    template_key_map = template_key_map or {}
    strengths, developing, weaknesses = [], [], []
    buckets = {"strength": strengths, "developing": developing, "weakness": weaknesses}

    for name, d in dims.items():
        if d["status"] == Evidence.NOT_APPLICABLE:
            continue
        classification = _classify(d["score"], d["status"])
        template_key = template_key_map.get(name, name)
        ctx = {"score": round(d["score"]), **extra_ctx.get(name, {})}

        potential_total = _potential_if_full(dims, name)
        points_gain = round(max(0.0, potential_total - current_total), 2)

        buckets[classification].append({
            "dimension": name,
            "label": _label(name, lang),
            "score": d["score"],
            "weight": d["weight"],
            "status": d["status"],
            "explanation": _render(EXPLANATIONS, template_key, classification, lang, ctx),
            "current_overall_score": current_total,
            "potential_overall_score": potential_total,
            "points_gain": points_gain,
            "how_to_improve": _render(ACTIONS, template_key, classification, lang, ctx),
        })

    strengths.sort(key=lambda i: i["score"], reverse=True)
    # Biggest points_gain first = fixing it moves the total score the most.
    developing.sort(key=lambda i: i["points_gain"], reverse=True)
    weaknesses.sort(key=lambda i: i["points_gain"], reverse=True)
    return {"strengths": strengths, "developing": developing, "weaknesses": weaknesses}


def _listed(items, limit=6):
    items = list(items or [])
    return ", ".join(items[:limit]) + ("..." if len(items) > limit else "")


def _top_opportunity(job_fit, general_employability, lang):
    candidates = [(i, "job_fit") for i in (job_fit["weaknesses"] + job_fit["developing"])]
    candidates += [(i, "general_employability") for i in
                   (general_employability["weaknesses"] + general_employability["developing"])]
    candidates = [c for c in candidates if c[0]["points_gain"] > 0]
    if not candidates:
        return None
    item, group = max(candidates, key=lambda c: c[0]["points_gain"])
    template = TOP_OPPORTUNITY_TEXT.get(lang, TOP_OPPORTUNITY_TEXT["en"])
    group_label = SCORE_GROUP_LABELS.get(group, {}).get(lang) or SCORE_GROUP_LABELS.get(group, {}).get("en", "")
    return template.format(
        label=item["label"], score_group=group_label,
        current=item["current_overall_score"], potential=item["potential_overall_score"],
        gain=item["points_gain"])


def build(job_match_score: dict, employability_index: dict, *, matched_skills=None,
          missing_skills=None, required_language=None, required_language_level=None,
          lang: str = "en") -> dict:
    """Build the candidate-facing strengths/weaknesses summary.

    ``job_match_score`` / ``employability_index`` are the dicts returned
    by ``scoring.job_match_score`` / ``scoring.european_employability_index``.
    ``matched_skills`` / ``missing_skills`` should be the already-relabelled
    (human-readable) lists, and ``required_language`` the display name of
    the language (e.g. "French"), so the copy reads naturally.
    """
    lang = _lang(lang)
    missing_skills = missing_skills or []

    job_ctx = {
        "skills": {
            "matched": len(matched_skills or []),
            "missing": len(missing_skills),
            "listed_missing": _listed(missing_skills),
        },
        "languages": {
            "language": required_language or "",
            "level": required_language_level or "",
        },
    }
    job_fit = _build_group(job_match_score["dimensions"], job_match_score["total"], lang, job_ctx)
    general_employability = _build_group(
        employability_index["dimensions"], employability_index["total"], lang, {},
        template_key_map={"skills": "general_skills", "languages": "general_language_level"})

    strong_count = len(job_fit["strengths"]) + len(general_employability["strengths"])
    weak_count = len(job_fit["weaknesses"]) + len(general_employability["weaknesses"])
    summary = SUMMARY_TEXT.get(lang, SUMMARY_TEXT["en"]).format(strong=strong_count, weak=weak_count)
    top_opportunity = _top_opportunity(job_fit, general_employability, lang)

    return {
        "job_fit": job_fit,
        "general_employability": general_employability,
        "summary": summary,
        "top_opportunity": top_opportunity,
    }