from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.crosswalk.models import EscoOccupation, OccupationSkill
from apps.crosswalk.serializers import OccupationSkillSerializer
from apps.crosswalk.i18n import normalize_lang, skill_label_map

_relation = openapi.Parameter(
    "relation", openapi.IN_QUERY,
    description="Filter by relation: essential | optional", type=openapi.TYPE_STRING)
_lang = openapi.Parameter("lang", openapi.IN_QUERY, description="Label language: en | es | pt",
                          type=openapi.TYPE_STRING)


@swagger_auto_schema(
    method="get",
    operation_id="occupation_skills",
    operation_summary="List skills of an ESCO occupation",
    manual_parameters=[_relation, _lang],
    responses={200: OccupationSkillSerializer(many=True), 404: "Not found"},
    tags=["Crosswalk"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def occupation_skills(request, esco_uuid):
    if not EscoOccupation.objects.filter(pk=esco_uuid).exists():
        return Response({"detail": "Occupation not found."},
                        status=status.HTTP_404_NOT_FOUND)
    qs = OccupationSkill.objects.filter(occupation_id=esco_uuid)
    relation = request.query_params.get("relation")
    if relation in (OccupationSkill.ESSENTIAL, OccupationSkill.OPTIONAL):
        qs = qs.filter(relation=relation)
    skills = list(qs)
    lang = normalize_lang(request.query_params.get("lang"))
    loc = skill_label_map([s.skill_uuid for s in skills], lang)
    data = OccupationSkillSerializer(skills, many=True).data
    for item, s in zip(data, skills):
        item["skill_label"] = loc.get(str(s.skill_uuid), item["skill_label"])
    return Response(data)