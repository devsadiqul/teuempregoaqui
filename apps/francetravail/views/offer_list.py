from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.crosswalk.models import EscoOccupation
from apps.candidate.services import occupation_label
from apps.francetravail.models import JobOffer
from apps.francetravail.serializers import JobOfferSerializer
from apps.francetravail.translate import translate, localize_contract

_rome = openapi.Parameter("rome", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          description="Filter by ROME metier code")
_resolved = openapi.Parameter("resolved", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description="true = only offers resolved to ESCO")
_limit = openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                           description="Max results (default 50)")
_lang = openapi.Parameter("lang", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          description="Display language: en | es | pt")


@swagger_auto_schema(
    method="get",
    operation_id="offer_list",
    operation_summary="List mirrored France Travail offers",
    manual_parameters=[_rome, _resolved, _limit, _lang],
    responses={200: JobOfferSerializer(many=True)},
    tags=["France Travail"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def offer_list(request):
    qs = JobOffer.objects.filter(is_active=True)
    rome = request.query_params.get("rome")
    if rome:
        qs = qs.filter(rome_code=rome)
    if request.query_params.get("resolved") == "true":
        qs = qs.filter(esco_uuid__isnull=False)
    try:
        limit = min(int(request.query_params.get("limit", 50)), 200)
    except ValueError:
        limit = 50

    lang = request.query_params.get("lang", "en")
    offers = list(qs.order_by("-last_seen")[:limit])
    data = JobOfferSerializer(offers, many=True).data

    uuids = [o.esco_uuid for o in offers if o.esco_uuid]
    occ_by_uuid = {str(o.pk): o for o in EscoOccupation.objects.filter(pk__in=uuids)}

    for item, offer in zip(data, offers):
        item["title"] = translate(item["title"], lang)
        item["description"] = translate(item["description"], lang)
        item["contract_type"] = localize_contract(item["contract_type"], lang)
        occ = occ_by_uuid.get(str(offer.esco_uuid)) if offer.esco_uuid else None
        item["esco_label"] = occupation_label(occ, lang) if occ else None

    return Response(data)