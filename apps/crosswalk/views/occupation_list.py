from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.crosswalk.models import EscoOccupation
from apps.crosswalk.serializers import EscoOccupationSerializer
from apps.crosswalk.i18n import normalize_lang

_q = openapi.Parameter("q", openapi.IN_QUERY, description="Search text (label or code)",
                       type=openapi.TYPE_STRING)
_limit = openapi.Parameter("limit", openapi.IN_QUERY, description="Max results (default 20)",
                           type=openapi.TYPE_INTEGER)
_lang = openapi.Parameter("lang", openapi.IN_QUERY, description="Label language: en | es | pt",
                          type=openapi.TYPE_STRING)


@swagger_auto_schema(
    method="get",
    operation_id="occupations_search",
    operation_summary="Search ESCO occupations",
    manual_parameters=[_q, _limit, _lang],
    responses={200: EscoOccupationSerializer(many=True)},
    tags=["Crosswalk"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def occupation_list(request):
    lang = normalize_lang(request.query_params.get("lang"))
    qs = EscoOccupation.objects.all()
    q = request.query_params.get("q", "").strip()
    if q:
        qs = (qs.filter(label__icontains=q) | qs.filter(label_es__icontains=q)
              | qs.filter(label_pt__icontains=q) | qs.filter(code__icontains=q))
    try:
        limit = min(int(request.query_params.get("limit", 20)), 100)
    except ValueError:
        limit = 20
    occs = list(qs.distinct()[:limit])
    data = EscoOccupationSerializer(occs, many=True).data
    for item, occ in zip(data, occs):
        item["label"] = occ.localized_label(lang)
    return Response(data, status=status.HTTP_200_OK)