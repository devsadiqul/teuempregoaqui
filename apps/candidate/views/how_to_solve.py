from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.candidate import resolutions, services
from apps.candidate.serializers import HowToSolveRequestSerializer
from apps.candidate.response_schemas import HowToSolveReportSchema


@swagger_auto_schema(
    method="post",
    operation_id="how_to_solve",
    operation_summary="Resolution guidance for a gap (single) or all gaps (full report)",
    request_body=HowToSolveRequestSerializer,
    responses={200: HowToSolveReportSchema,
               400: "Validation error", 404: "Profile/occupation not found"},
    tags=["Matching"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def how_to_solve(request):
    req = HowToSolveRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    d = req.validated_data
    lang = d.get("lang") or "en"

    if d.get("profile_id") and not d.get("gap_type"):
        profile = services.get_visible_profile(request, d["profile_id"])
        if profile is None:
            return Response({"detail": "Profile not found or not accessible."},
                            status=status.HTTP_404_NOT_FOUND)
        occupation = services.resolve_occupation(
            d.get("esco_uuid"), d.get("rome_appellation_id"))
        if occupation is None:
            return Response({"detail": "Target occupation not found."},
                            status=status.HTTP_404_NOT_FOUND)
        result = services.run_match(profile, occupation, d, lang=lang)
        profile_country_code = profile.target_country.country_code if profile.target_country else None
        country = (d.get("target_country") or profile_country_code or "ES").upper()
        current = result["total"]
        cards = [resolutions.resolve(a["gap_type"], country, a.get("context", {}),
                                     current, a["gain"], lang=lang)
                 for a in result["evolution"]["actions"]]
        # Mandatory eligibility gaps (priority_level 5, gain 0) sort first -
        # they block the vacancy outright, regardless of score impact.
        cards.sort(key=lambda c: (c["priority_level"], c["expected_impact_points"]), reverse=True)
        return Response({
            "total": current, "classification": result["classification"],
            "potential": result["evolution"]["potential"],
            "target": result["target"], "how_to_solve": cards})

    try:
        card = resolutions.resolve(
            gap_type=d["gap_type"], target_country=d["target_country"].upper(),
            context=d.get("context", {}), current_score=d.get("current_score"),
            gain=d.get("gain", 0.0), lang=lang)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(card)