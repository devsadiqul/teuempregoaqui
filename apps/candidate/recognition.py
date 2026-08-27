"""
Automatic determination of professional-recognition requirements.

Per client feedback (Breafing_ago_26): the platform must not ask users
whether their qualification is "recognized" - it must work this out for
them from official/public sources and report one of three states:

    REQUIRED / NOT IDENTIFIED AS REQUIRED / FURTHER VERIFICATION REQUIRED

This module is a rules engine over the country -> competent-authority
map already used for recommendation cards (`resolutions.DEGREE_RECOGNITION`),
combined with the ESCO `regulated` flag on the target occupation. It is
deliberately conservative: it never claims a requirement is "not required"
just because our authority dataset is incomplete - it reports "further
verification required" instead. This is informational output, not an
individualized legal opinion (TeuEmpregoAqui does not determine
immigration/legal status - detailed guidance belongs to future
integrations, e.g. TuamigracaoAqui).

Extending country coverage: add an entry to `resolutions.DEGREE_RECOGNITION`
(and `regulated_occupation_codes` below, if the profession also needs a
specific licensing body beyond general diploma recognition) - no scoring
logic needs to change.
"""

from apps.candidate.resolutions import DEGREE_RECOGNITION
from apps.candidate.resolution_text import FALLBACK_INSTITUTION
from apps.candidate.models import PracticeCredential

Requirement = PracticeCredential.RecognitionRequirement

# Occupations where recognition is required via a specific professional
# licensing/registration body (beyond general academic diploma recognition),
# keyed by ESCO ISCO group prefix. Extend as more regulated professions are
# confirmed with an official source.
REGULATED_LICENSING_BODY = {
    "PT": {"221": ("Ordem dos Medicos", "https://ordemdosmedicos.pt"),
           "222": ("Ordem dos Enfermeiros", "https://www.ordemenfermeiros.pt")},
    "ES": {"221": ("Consejo General de Colegios de Medicos", "https://www.cgcom.es"),
           "222": ("Consejo General de Enfermeria", "https://www.consejogeneralenfermeria.org")},
    "FR": {"221": ("Conseil National de l'Ordre des Medecins", "https://www.conseil-national.medecin.fr"),
           "222": ("Ordre National des Infirmiers", "https://www.ordre-infirmiers.fr")},
    "DE": {"221": ("Bundesarztekammer", "https://www.bundesaerztekammer.de"),
           "222": ("Pflegekammer (Landesebene)", "https://www.bundesgesundheitsministerium.de")},
    "IT": {"221": ("Federazione Nazionale degli Ordini dei Medici (FNOMCeO)", "https://portale.fnomceo.it"),
           "222": ("Federazione Nazionale degli Ordini delle Professioni Infermieristiche",
                   "https://www.fnopi.it")},
}


def determine_recognition_requirement(occupation, country_code: str) -> dict:
    """Returns {"status": Requirement, "competent_authority": str,
    "official_source_url": str, "evidence_status": "verified"|"declared_unverified"}.

    Rules (evaluated in order):
    1. Occupation not flagged as regulated in ESCO -> NOT_IDENTIFIED_AS_REQUIRED.
    2. Occupation regulated AND a specific licensing body is known for this
       country/ISCO-group -> REQUIRED, with that body cited.
    3. Occupation regulated AND only a general diploma-recognition authority
       is known for this country -> REQUIRED, with that authority cited
       (recognition is a prerequisite even where no separate professional
       order applies).
    4. Occupation regulated but no authority is known for this country in
       our dataset -> FURTHER_VERIFICATION_REQUIRED (never silently
       downgraded to "not required" - absence of data is not evidence of
       absence of a requirement).
    """
    country = (country_code or "").upper()
    regulated = bool(getattr(occupation, "regulated", False))

    if not regulated:
        return {"status": Requirement.NOT_IDENTIFIED_AS_REQUIRED,
                "competent_authority": "", "official_source_url": "",
                "evidence_status": "declared_unverified"}

    isco_prefix = (getattr(occupation, "isco_group", "") or "")[:3]
    licensing = REGULATED_LICENSING_BODY.get(country, {}).get(isco_prefix)
    if licensing:
        authority, url = licensing
        return {"status": Requirement.REQUIRED,
                "competent_authority": authority, "official_source_url": url,
                "evidence_status": "verified"}

    general = DEGREE_RECOGNITION.get(country)
    if general:
        authority, url = general
        return {"status": Requirement.REQUIRED,
                "competent_authority": authority, "official_source_url": url,
                "evidence_status": "verified"}

    return {"status": Requirement.FURTHER_VERIFICATION_REQUIRED,
            "competent_authority": FALLBACK_INSTITUTION["degree_recognition"]["en"],
            "official_source_url": "", "evidence_status": "declared_unverified"}


def sync_practice_credential(profile, occupation, country) -> "PracticeCredential":
    """Idempotently create/update the PracticeCredential row for this
    profile+country with the system-determined recognition requirement,
    without touching the user's own self-declared recognition_status /
    regulated_profession_status fields."""
    result = determine_recognition_requirement(occupation, getattr(country, "country_code", country))
    cred, _ = PracticeCredential.objects.get_or_create(profile=profile, country=country)
    cred.recognition_requirement_status = result["status"]
    cred.competent_authority = result["competent_authority"]
    cred.official_source_url = result["official_source_url"]
    cred.save(update_fields=["recognition_requirement_status", "competent_authority",
                             "official_source_url"])
    return cred