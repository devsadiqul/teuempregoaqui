from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.candidate.serializers import CandidateProfileSerializer
from apps.candidate import services


@swagger_auto_schema(
    method="get",
    operation_id="candidate_review",
    operation_summary="Pre-submission review summary (Final Review step)",
    responses={200: "Review summary", 404: "Profile not found"},
    tags=["Candidate"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def profile_review(request, pk):
    """Backend support for the client-requested Final Review step: lets the
    user see and correct their information before completing the
    assessment, with the Privacy Notice/Terms acceptance shown separately
    from optional consents (e.g. marketing). Returns the full profile plus
    a section-by-section readiness summary; no frontend screen is included
    in this delivery - the frontend team renders the review UI from this
    payload."""
    profile = services.get_visible_profile(request, pk)
    if profile is None:
        return Response({"detail": "Profile not found or not accessible."},
                        status=status.HTTP_404_NOT_FOUND)

    return Response({
        "profile": CandidateProfileSerializer(profile).data,
        "review": services.review_summary(profile),
    })