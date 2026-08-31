from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.candidate.models import Nationality
from apps.candidate.serializers import NationalitySerializer

DEFAULT_LIMIT = 20
MAX_LIMIT = 100
SUPPORTED_LANGS = {"en", "es", "pt"}


@swagger_auto_schema(
    method="get",
    operation_id="nationality_list",
    operation_summary="Search/autocomplete nationalities (demonyms) by country or demonym name",
    manual_parameters=[
        openapi.Parameter(
            "search", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
            description="Free-text match against country name or demonym (en/es/pt). Omit to list all.",
        ),
        openapi.Parameter(
            "limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
            description=f"Max rows to return (default {DEFAULT_LIMIT}, max {MAX_LIMIT}).",
        ),
        openapi.Parameter(
            "lang", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
            description="en, es or pt to collapse the response to a single "
                        "locale-appropriate `demonym` field. Omit for the default "
                        "demonym plus demonym_es/demonym_pt together.",
        ),
    ],
    responses={200: NationalitySerializer(many=True)},
    tags=["Candidate"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def nationality_list(request):
    search = request.query_params.get("search", "").strip()

    try:
        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    limit = max(1, min(limit, MAX_LIMIT))

    lang = request.query_params.get("lang", "").strip().lower()
    if lang not in SUPPORTED_LANGS:
        lang = None

    qs = Nationality.objects.select_related("location")
    if search:
        qs = qs.filter(
            Q(location__name__istartswith=search)
            | Q(demonym__istartswith=search)
            | Q(demonym_es__istartswith=search)
            | Q(demonym_pt__istartswith=search)
        )
    qs = qs.order_by("location__name")[:limit]

    serializer = NationalitySerializer(qs, many=True, context={"lang": lang})
    return Response(serializer.data)