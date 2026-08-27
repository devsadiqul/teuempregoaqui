import unicodedata

from .models import Location

COUNTRY_ALIASES = {
    "brasil": "Brazil", "brazil": "Brazil", "brazilian": "Brazil",
    "usa": "United States", "us": "United States", "united states": "United States",
    "united states of america": "United States", "american": "United States", "eua": "United States",
    "uk": "United Kingdom", "england": "United Kingdom", "britain": "United Kingdom",
    "great britain": "United Kingdom", "british": "United Kingdom",
    "portugal": "Portugal", "portuguese": "Portugal",
    "espanha": "Spain", "espana": "Spain", "spain": "Spain", "spanish": "Spain",
    "franca": "France", "france": "France", "french": "France",
    "alemanha": "Germany", "germany": "Germany", "german": "Germany", "deutschland": "Germany",
    "italia": "Italy", "italy": "Italy", "italian": "Italy",
}


def _normalize(value):
    value = value.strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c)
    )


def match_country(raw_value, cache=None):
    if not raw_value or not raw_value.strip():
        return None

    normalized = _normalize(raw_value)
    if cache is not None and normalized in cache:
        return cache[normalized]

    canonical = COUNTRY_ALIASES.get(normalized, raw_value.strip())
    location = Location.objects.filter(location_type="country", name__iexact=canonical).first()

    if cache is not None:
        cache[normalized] = location
    return location