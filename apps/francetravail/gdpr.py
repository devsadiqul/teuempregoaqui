import re

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

PHONE_RE = re.compile(
    r"(?<!\d)(?:(?:\+|00)\d{1,3}[\s.\-]*(?:\(?\d{1,4}\)?[\s.\-]*){2,5}\d{2,4}"
    r"|0\d(?:[\s.\-]?\d{2}){4})(?!\d)"
)
URL_CONTACT_RE = re.compile(r"\bmailto:\S+", re.IGNORECASE)


def sanitize_text(text: str) -> str:
    if not text:
        return text
    text = EMAIL_RE.sub("[email removed]", text)
    text = URL_CONTACT_RE.sub("[contact removed]", text)
    text = PHONE_RE.sub("[phone removed]", text)
    return text


def sanitize_offer(offer: dict) -> dict:

    entreprise = offer.get("entreprise", {}) or {}
    lieu = offer.get("lieuTravail", {}) or {}
    salaire = offer.get("salaire", {}) or {}
    origine = offer.get("origineOffre", {}) or {}

    return {
        "source_id": offer.get("id"),
        "title": offer.get("intitule", ""),
        "description": sanitize_text(offer.get("description", "")),
        "rome_code": offer.get("romeCode", ""),
        "rome_label": offer.get("romeLibelle", ""),
        "appellation_label": offer.get("appellationlibelle", ""),
        "appellation_code": str(offer.get("codeAppellation") or ""),
        "contract_type": offer.get("typeContratLibelle", ""),
        "company_name": entreprise.get("nom", ""),
        "location": lieu.get("libelle", ""),
        "department": (lieu.get("codePostal", "") or "")[:2],
        "salary": sanitize_text(salaire.get("libelle", "")),
        "source_url": origine.get("urlOrigine", ""),
        "posted_at": offer.get("dateCreation"),
        "updated_at": offer.get("dateActualisation"),
    }
