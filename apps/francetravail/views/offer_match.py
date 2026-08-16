from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.candidate import services as candidate_services
from apps.candidate.response_schemas import OfferMatchResponseSchema
from apps.francetravail import services as ft_services
from apps.francetravail.models import JobOffer
from apps.francetravail.serializers import OfferMatchRequestSerializer
from apps.francetravail.translate import translate

_lang = openapi.Parameter("lang", openapi.IN_QUERY, description="Label language: en | es | pt",
                          type=openapi.TYPE_STRING)


@swagger_auto_schema(
    method="post",
    operation_id="offer_match",
    operation_summary="Score a candidate against a live France Travail offer",
    request_body=OfferMatchRequestSerializer,
    manual_parameters=[_lang],
    responses={200: OfferMatchResponseSchema, 404: "Offer or profile not found"},
    tags=["France Travail"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def offer_match(request, source_id):
    req = OfferMatchRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    d = req.validated_data
    lang = request.query_params.get("lang") or request.data.get("lang") or "en"

    offer = JobOffer.objects.filter(source_id=source_id, is_active=True).first()
    if offer is None:
        return Response({"detail": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

    profile = candidate_services.get_visible_profile(request, d["profile_id"])
    if profile is None:
        return Response({"detail": "Profile not found or not accessible."},
                        status=status.HTTP_404_NOT_FOUND)

    clean = {
        "source_id": offer.source_id, "title": offer.title,
        "company_name": offer.company_name, "location": offer.location,
        "rome_code": offer.rome_code, "source_url": offer.source_url,
        "appellation_code": "", "appellation_label": offer.appellation_label,
    }
    candidate_input = candidate_services.candidate_input_from_profile(
        profile, experience_relevance=d["experience_relevance"],
        field_relevance=d["field_relevance"])
    result = ft_services.match_candidate_to_offer(
        candidate_input, clean, lang=lang,
        required_language_level=d.get("required_language_level"),
        local_language=d.get("local_language", "required"))
    result["offer"]["title"] = translate(result["offer"]["title"], lang)
    return Response(result)