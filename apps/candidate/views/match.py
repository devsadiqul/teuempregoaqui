from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.candidate.serializers import MatchRequestSerializer
from apps.candidate.response_schemas import MatchResponseSchema
from apps.candidate import services

_lang = openapi.Parameter("lang", openapi.IN_QUERY, description="Label language: en | es | pt",
                          type=openapi.TYPE_STRING)


@swagger_auto_schema(
    method="post",
    operation_id="match",
    operation_summary="Score a candidate against a target occupation",
    request_body=MatchRequestSerializer,
    manual_parameters=[_lang],
    responses={200: MatchResponseSchema, 404: "Profile or occupation not found"},
    tags=["Matching"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def match(request):
    req = MatchRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    data = req.validated_data
    lang = request.query_params.get("lang") or request.data.get("lang") or "en"

    profile = services.get_visible_profile(request, data["profile_id"])
    if profile is None:
        return Response({"detail": "Profile not found or not accessible."},
                        status=status.HTTP_404_NOT_FOUND)

    occupation = services.resolve_occupation(
        data.get("esco_uuid"), data.get("rome_appellation_id"))
    if occupation is None:
        return Response({"detail": "Target occupation not found."},
                        status=status.HTTP_404_NOT_FOUND)

    return Response(services.run_match(profile, occupation, data, lang=lang))