from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.candidate.models import CandidateProfile
from apps.candidate.serializers import CandidateProfileSerializer
from apps.candidate import services


@swagger_auto_schema(method="get", operation_id="candidate_retrieve",
                     operation_summary="Retrieve a candidate profile",
                     responses={200: CandidateProfileSerializer, 404: "Not found"},
                     tags=["Candidate"])
@swagger_auto_schema(method="put", operation_id="candidate_update",
                     operation_summary="Replace a candidate profile",
                     request_body=CandidateProfileSerializer,
                     responses={200: CandidateProfileSerializer}, tags=["Candidate"])
@swagger_auto_schema(method="patch", operation_id="candidate_partial_update",
                     operation_summary="Partially update a candidate profile",
                     request_body=CandidateProfileSerializer,
                     responses={200: CandidateProfileSerializer}, tags=["Candidate"])
@swagger_auto_schema(method="delete", operation_id="candidate_delete",
                     operation_summary="Delete a candidate profile",
                     responses={204: "Deleted", 404: "Not found"}, tags=["Candidate"])
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def profile_detail(request, pk):
    profile = services.get_visible_profile(request, pk)
    if profile is None:
        return Response({"detail": "Profile not found or not accessible."},
                        status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(CandidateProfileSerializer(profile).data)

    if request.method in ("PUT", "PATCH"):
        serializer = CandidateProfileSerializer(
            profile, data=request.data, partial=(request.method == "PATCH"))
        serializer.is_valid(raise_exception=True)

        target_mode = serializer.validated_data.get("mode", profile.mode)
        user = getattr(request, "user", None)
        is_authenticated = user is not None and user.is_authenticated

        if target_mode == CandidateProfile.Mode.ACCOUNT:
            if not is_authenticated:
                raise PermissionDenied("Personal Account Mode requires authentication.")
            serializer.save(user_id=str(user.id))
        else:
            serializer.save()
        return Response(serializer.data)

    profile.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)