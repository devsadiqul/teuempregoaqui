from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.crosswalk.models import EscoOccupation
from apps.crosswalk.serializers import EscoOccupationSerializer
from apps.crosswalk.i18n import normalize_lang

_lang = openapi.Parameter("lang", openapi.IN_QUERY, description="Label language: en | es | pt",
                          type=openapi.TYPE_STRING)


@swagger_auto_schema(
    method="get",
    operation_id="occupation_detail",
    operation_summary="Retrieve one ESCO occupation",
    manual_parameters=[_lang],
    responses={200: EscoOccupationSerializer, 404: "Not found"},
    tags=["Crosswalk"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def occupation_detail(request, esco_uuid):
    occ = EscoOccupation.objects.filter(pk=esco_uuid).first()
    if occ is None:
        return Response({"detail": "Occupation not found."},
                        status=status.HTTP_404_NOT_FOUND)
    lang = normalize_lang(request.query_params.get("lang"))
    data = EscoOccupationSerializer(occ).data
    data["label"] = occ.localized_label(lang)
    return Response(data)