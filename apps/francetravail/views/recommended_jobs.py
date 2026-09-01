import logging
from collections import defaultdict

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.crosswalk.models import EscoOccupation
from apps.candidate import scoring
from apps.candidate import services as candidate_services
from apps.candidate.response_schemas import RecommendResponseSchema
from apps.francetravail.models import JobOffer
from apps.francetravail.serializers import RecommendRequestSerializer
from apps.francetravail.translate import translate

logger = logging.getLogger(__name__)


def safe_translate(text, lang):
    """Try to translate; on any failure, return the original text unchanged."""
    if not text:
        return text
    try:
        result = translate(text, lang)
        return result or text
    except Exception as e:
        logger.warning("Translation skipped, returning original text: %s", e)
        return text


@swagger_auto_schema(
    method="post",
    operation_id="recommended_jobs",
    operation_summary="Rank live jobs by compatibility for a candidate profile",
    request_body=RecommendRequestSerializer,
    responses={200: RecommendResponseSchema, 404: "Profile not found"},
    tags=["France Travail"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def recommended_jobs(request):
    req = RecommendRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    d = req.validated_data
    lang = d["lang"]
    local_language = d["local_language"]
    required_language = "French" if local_language != "none" else None

    profile = candidate_services.get_visible_profile(request, d["profile_id"])
    if profile is None:
        return Response({"detail": "Profile not found or not accessible."},
                        status=status.HTTP_404_NOT_FOUND)

    offers = JobOffer.objects.filter(is_active=True, esco_uuid__isnull=False)
    if d.get("departement"):
        offers = offers.filter(department=d["departement"])

    by_occupation = defaultdict(list)
    for offer in offers.only(
        "source_id", "title", "description", "company_name",
        "location", "rome_code", "source_url", "esco_uuid",
    ):
        by_occupation[str(offer.esco_uuid)].append(offer)

    # in_bulk() keys UUIDField results by uuid.UUID objects, not strings —
    # normalize to str so lookups with by_occupation's string keys work.
    occupations = {
        str(k): v for k, v in EscoOccupation.objects.in_bulk(by_occupation.keys()).items()
    }

    candidate_input = candidate_services.candidate_input_from_profile(
        profile, experience_relevance=d["experience_relevance"],
        field_relevance=d["field_relevance"])

    scored = []
    for esco_uuid, offer_list in by_occupation.items():
        occupation = occupations.get(esco_uuid)
        if occupation is None:
            continue
        essential_map = candidate_services.essential_skill_map(occupation, lang)
        esco_label = candidate_services.occupation_label(occupation, lang)
        regulated = bool(getattr(occupation, "regulated", False))
        required_skills = list(essential_map.keys())

        for offer in offer_list:
            vacancy = scoring.VacancyInput(
                required_skills=required_skills,
                required_language=required_language,
                local_language=local_language,
                regulated=regulated,
                location=offer.location or None,
            )
            result = scoring.score(candidate_input, vacancy)
            if result["total"] < d["min_score"]:
                continue
            missing = [essential_map.get(u, u) for u in result["missing_skills"]]
            scored.append((result["total"], offer, result, missing, esco_label))

    scored.sort(key=lambda r: r[0], reverse=True)
    scored = scored[:d["limit"]]

    recommended = []
    for score_val, offer, result, missing, esco_label in scored:
        recommended.append({
            "source_id": offer.source_id,
            "title": safe_translate(offer.title, lang),
            "description": safe_translate(offer.description, lang),
            "company_name": offer.company_name,
            "location": offer.location,
            "rome_code": offer.rome_code,
            "source_url": offer.source_url,
            "esco_label": esco_label,
            "score": score_val,
            "classification": result["classification"],
            "potential": result["evolution"]["potential"],
            "missing_skills": missing,
        })

    return Response({"count": len(recommended), "recommended": recommended})