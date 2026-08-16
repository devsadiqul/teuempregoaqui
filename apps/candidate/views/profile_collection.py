from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.candidate.models import CandidateProfile
from apps.candidate.serializers import CandidateProfileSerializer
from apps.candidate import services


@swagger_auto_schema(
    method="get",
    operation_id="candidate_list",
    operation_summary="List visible candidate profiles",
    responses={200: CandidateProfileSerializer(many=True)},
    tags=["Candidate"],
)
@swagger_auto_schema(
    method="post",
    operation_id="candidate_create",
    operation_summary="Create a candidate profile (8-section form)",
    request_body=CandidateProfileSerializer,
    responses={201: CandidateProfileSerializer, 400: "Validation error"},
    tags=["Candidate"],
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def profile_collection(request):
    if request.method == "GET":
        qs = services.visible_profiles(request)
        return Response(CandidateProfileSerializer(qs, many=True).data)

    serializer = CandidateProfileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    mode = serializer.validated_data.get("mode", CandidateProfile.Mode.PRIVATE)
    if mode == CandidateProfile.Mode.ACCOUNT:
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise PermissionDenied("Personal Account Mode requires authentication.")
        serializer.save(user_id=str(user.id))
    else:
        serializer.save(session_key=services.session_key(request))
    return Response(serializer.data, status=status.HTTP_201_CREATED)