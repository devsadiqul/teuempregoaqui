from apps.candidate.resolution_text import (
    TEXT, DISCLAIMER, NONE_LABEL, IMPACT_LABELS, LANGUAGE_NAMES,
    FALLBACK_INSTITUTION, DOC_INSTITUTION,
)

DEGREE_RECOGNITION = {
    "PT": ("DGES - Direcao-Geral do Ensino Superior", "https://www.dges.gov.pt"),
    "ES": ("Ministerio de Ciencia, Innovacion y Universidades - Homologacion",
           "https://www.universidades.gob.es"),
    "FR": ("ENIC-NARIC France", "https://www.france-education-international.fr/enic-naric-france"),
    "DE": ("ZAB / anabin (Zentralstelle fur auslandisches Bildungswesen)",
           "https://anabin.kmk.org"),
    "IT": ("CIMEA - Centro di Informazione su Mobilita e Equivalenze Accademiche",
           "https://www.cimea.it"),
}

IMMIGRATION = {
    "PT": ("AIMA - Agencia para a Integracao, Migracoes e Asilo", "https://aima.gov.pt"),
    "ES": ("Oficina de Extranjeria - Ministerio de Inclusion",
           "https://extranjeros.inclusion.gob.es"),
    "FR": ("OFII / Prefecture - Administration etrangers en France",
           "https://administration-etrangers-en-france.interieur.gouv.fr"),
    "DE": ("BAMF - Bundesamt fur Migration und Fluchtlinge", "https://www.bamf.de"),
    "IT": ("Sportello Unico per l'Immigrazione - Ministero dell'Interno",
           "https://www.interno.gov.it"),
}

LANGUAGE_INSTITUTES = {
    "spanish": ("Instituto Cervantes", "https://www.cervantes.es"),
    "portuguese": ("Instituto Camoes", "https://www.instituto-camoes.pt"),
    "french": ("Alliance Francaise", "https://www.alliancefr.org"),
    "german": ("Goethe-Institut", "https://www.goethe.de"),
    "italian": ("Societa Dante Alighieri", "https://ladante.it"),
}

COUNTRY_LANGUAGE = {"PT": "portuguese", "ES": "spanish", "FR": "french",
                    "DE": "german", "IT": "italian"}

SKILLS_PORTAL = ("Europass / EU course catalogue", "https://europass.europa.eu")


def _priority(gain: float) -> int:
    if gain >= 10:
        return 5
    if gain >= 6:
        return 4
    if gain >= 3:
        return 3
    if gain > 0:
        return 2
    return 1


def _projected(current, gain):
    if current is None:
        return None
    after = round(min(100.0, current + gain), 1)
    return f"{current}% -> {after}%"


def _card(gap_type, lang, fmt, inst, url, extra=None):
    t = TEXT[gap_type].get(lang, TEXT[gap_type]["en"])
    card = {
        "title": t["title"].format(**fmt),
        "explanation": t["explanation"].format(**fmt),
        "recommended_actions": [a.format(**fmt) for a in t["recommended_actions"]],
        "estimated_timeline": t["estimated_timeline"],
        "estimated_cost": t["estimated_cost"],
        "institution": inst,
        "official_link": url,
        "goal": t["goal"].format(**fmt),
    }
    if extra:
        card.update(extra)
    return card


def _resolve_language(country, ctx, lang):
    key = (ctx.get("language") or COUNTRY_LANGUAGE.get(country, "")).lower()
    pair = LANGUAGE_INSTITUTES.get(key)
    inst, url = pair if pair else (FALLBACK_INSTITUTION["language"][lang], "")
    name = LANGUAGE_NAMES.get(key, {}).get(lang, key.title() or "")
    fmt = {"language": name,
           "cur": ctx.get("current_level") or NONE_LABEL[lang],
           "target": ctx.get("target_level", "B2")}
    return _card("language", lang, fmt, inst, url)


def _resolve_immigration(country, ctx, lang):
    pair = IMMIGRATION.get(country)
    inst, url = pair if pair else (FALLBACK_INSTITUTION["immigration"][lang], "")
    return _card("immigration", lang, {}, inst, url)


def _resolve_degree_recognition(country, ctx, lang):
    pair = DEGREE_RECOGNITION.get(country)
    inst, url = pair if pair else (FALLBACK_INSTITUTION["degree_recognition"][lang], "")
    return _card("degree_recognition", lang, {}, inst, url)


def _resolve_skills(country, ctx, lang):
    inst, url = SKILLS_PORTAL
    missing = ctx.get("missing_skills", [])
    listed = ", ".join(missing[:6]) + ("..." if len(missing) > 6 else "")
    fmt = {"count": len(missing), "listed": listed}
    return _card("skills", lang, fmt, inst, url, extra={"missing_skills": missing})


def _resolve_documentation(country, ctx, lang):
    return _card("documentation", lang, {}, DOC_INSTITUTION[lang], "")


_RESOLVERS = {
    "language": _resolve_language,
    "immigration": _resolve_immigration,
    "degree_recognition": _resolve_degree_recognition,
    "skills": _resolve_skills,
    "documentation": _resolve_documentation,
}

VALID_GAP_TYPES = tuple(_RESOLVERS)


def resolve(gap_type, target_country, context=None, current_score=None,
            gain=0.0, lang="en"):
    context = context or {}
    lang = lang if lang in ("en", "es", "pt") else "en"
    resolver = _RESOLVERS.get(gap_type)
    if resolver is None:
        raise ValueError(f"Unknown gap_type '{gap_type}'. "
                         f"Expected one of {VALID_GAP_TYPES}.")
    card = resolver(target_country, context, lang)
    stars = _priority(gain)
    card.update({
        "gap_type": gap_type,
        "target_country": target_country,
        "priority_level": stars,
        "impact": IMPACT_LABELS[lang][stars],
        "expected_impact_points": round(gain, 2),
        "projected_compatibility": _projected(current_score, gain),
        "data_disclaimer": DISCLAIMER[lang],
    })
    return card