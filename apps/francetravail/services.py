import unicodedata
from functools import lru_cache
from django.utils import timezone
from apps.crosswalk.models import EscoOccupation, RomeEscoMapping
from apps.candidate import scoring
from apps.candidate import services as candidate_services
from .client import OffresClient
from .gdpr import sanitize_offer
from .models import JobOffer


def _norm_label(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(s.lower().split())


@lru_cache(maxsize=1)
def _label_index() -> dict:
    idx = {}
    for label, uuid in RomeEscoMapping.objects.values_list("rome_label", "occupation_id"):
        key = _norm_label(label)
        if key:
            idx.setdefault(key, uuid)
    return idx


def resolve_esco_uuid(appellation_code: str = None, appellation_label: str = None):
    if appellation_code:
        m = (RomeEscoMapping.objects
             .filter(rome_appellation_id=appellation_code)
             .values_list("occupation_id", flat=True).first())
        if m:
            return m
    if appellation_label:
        return _label_index().get(_norm_label(appellation_label))
    return None


def match_candidate_to_offer(candidate_input: scoring.CandidateInput, clean: dict, *,
                             lang="en", required_language=None,
                             required_language_level=None, local_language="required") -> dict:
    esco_uuid = resolve_esco_uuid(clean.get("appellation_code"),
                                  clean.get("appellation_label"))
    occ = EscoOccupation.objects.filter(pk=esco_uuid).first() if esco_uuid else None
    skill_map = candidate_services.essential_skill_map(occ, lang) if occ else {}
    vac = scoring.VacancyInput(
        required_skills=list(skill_map.keys()),
        required_language=required_language or ("French" if local_language != "none" else None),
        required_language_level=required_language_level,
        local_language=local_language,
    )
    result = scoring.score(candidate_input, vac)
    candidate_services._relabel_skills(result, skill_map)
    result["offer"] = {
        "source_id": clean.get("source_id"),
        "title": clean.get("title"),
        "company": clean.get("company_name"),
        "location": clean.get("location"),
        "rome_code": clean.get("rome_code"),
        "source_url": clean.get("source_url"),
        "esco_uuid": str(esco_uuid) if esco_uuid else None,
        "esco_label": candidate_services.occupation_label(occ, lang) if occ else None,
        "resolved_to_esco": esco_uuid is not None,
    }
    return result


def sync_offers(*, code_rome=None, mots_cles=None, departement=None,
                max_offers=150, client: OffresClient = None) -> dict:
    client = client or OffresClient()
    seen_ids, created, updated = [], 0, 0
    start = 0
    page = 49
    while start < max_offers:
        batch = client.search(code_rome=code_rome, mots_cles=mots_cles,
                              departement=departement,
                              range_start=start, range_end=start + page)
        offres = batch.get("offres", [])
        if not offres:
            break
        for raw in offres:
            clean = sanitize_offer(raw)
            if not clean["source_id"]:
                continue
            esco_uuid = resolve_esco_uuid(clean["appellation_code"],
                                          clean["appellation_label"])
            obj, was_created = JobOffer.objects.update_or_create(
                source_id=clean["source_id"],
                defaults={
                    "source": "france_travail",
                    "source_url": clean["source_url"],
                    "title": clean["title"][:255],
                    "description": clean["description"],
                    "rome_code": clean["rome_code"],
                    "rome_label": clean["rome_label"][:255],
                    "appellation_code": clean["appellation_code"],
                    "appellation_label": clean["appellation_label"][:255],
                    "esco_uuid": esco_uuid,
                    "contract_type": clean["contract_type"][:80],
                    "company_name": clean["company_name"][:255],
                    "location": clean["location"][:120],
                    "department": clean["department"],
                    "salary": clean["salary"][:255],
                    "posted_at": clean["posted_at"] or "",
                    "is_active": True,
                },
            )
            seen_ids.append(obj.source_id)
            created += int(was_created)
            updated += int(not was_created)
        if len(offres) < (page + 1):
            break
        start += page + 1

    return {"created": created, "updated": updated, "seen": len(seen_ids),
            "seen_ids": seen_ids}


def purge_stale(active_ids, older_than_days=30) -> int:
    cutoff = timezone.now() - timezone.timedelta(days=older_than_days)
    stale = JobOffer.objects.filter(source="france_travail").exclude(source_id__in=active_ids)
    stale = stale.filter(last_seen__lt=cutoff) | stale.filter(is_active=True, last_seen__lt=cutoff)
    count = stale.distinct().count()
    stale.distinct().delete()
    return count