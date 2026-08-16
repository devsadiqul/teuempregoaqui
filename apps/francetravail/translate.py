import hashlib
from django.conf import settings

CONTRACT_LABELS = {
    "CDI": {"en": "Permanent contract", "es": "Contrato indefinido", "pt": "Contrato sem termo"},
    "CDD": {"en": "Fixed-term contract", "es": "Contrato temporal", "pt": "Contrato a termo"},
    "MIS": {"en": "Temporary assignment", "es": "Mision temporal", "pt": "Missao temporaria"},
    "SAI": {"en": "Seasonal contract", "es": "Contrato de temporada", "pt": "Contrato sazonal"},
    "LIB": {"en": "Self-employed", "es": "Autonomo", "pt": "Trabalho independente"},
    "FRA": {"en": "Franchise", "es": "Franquicia", "pt": "Franquia"},
}

TRANSLATABLE_LANGS = ("en", "es", "pt")

_DEEPL_TARGET = {"en": "EN-GB", "es": "ES", "pt": "PT-PT"}


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def localize_contract(contract_type, lang):
    if not contract_type:
        return contract_type
    entry = CONTRACT_LABELS.get(contract_type.strip().upper())
    if entry:
        return entry.get(lang, entry.get("en", contract_type))
    return contract_type


def _provider_translate(text, lang):
    import requests
    key = getattr(settings, "DEEPL_API_KEY", "")
    if not key:
        return None
    url = getattr(settings, "DEEPL_API_URL", "https://api-free.deepl.com/v2/translate")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"DeepL-Auth-Key {key}",
    }
    payload = {
        "text": [text],
        "source_lang": "FR",
        "target_lang": _DEEPL_TARGET.get(lang, lang.upper()),
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["translations"][0]["text"]


def translate(text, lang):
    lang = (lang or "en").lower()[:2]
    if not text or lang not in TRANSLATABLE_LANGS:
        return text
    from .models import TranslationCache
    h = _hash(text)
    hit = TranslationCache.objects.filter(content_hash=h, target_lang=lang).first()
    if hit:
        return hit.translated
    try:
        out = _provider_translate(text, lang)
    except Exception:
        out = None
    if not out:
        return text
    TranslationCache.objects.update_or_create(
        content_hash=h, target_lang=lang, defaults={"translated": out})
    return out