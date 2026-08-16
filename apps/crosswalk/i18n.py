from apps.crosswalk.models import SkillLabel

SUPPORTED_LANGS = {"en", "es", "pt"}


def normalize_lang(lang):
    lang = (lang or "en").lower()[:2]
    return lang if lang in SUPPORTED_LANGS else "en"


def occupation_label(occupation, lang="en"):
    return occupation.localized_label(normalize_lang(lang))


def skill_label_map(skill_uuids, lang="en"):
    lang = normalize_lang(lang)
    if lang == "en":
        return {}
    rows = SkillLabel.objects.filter(lang=lang, skill_uuid__in=list(skill_uuids))
    return {str(r.skill_uuid): r.label for r in rows}