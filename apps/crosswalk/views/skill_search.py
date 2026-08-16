from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.crosswalk.models import OccupationSkill, SkillLabel
from apps.crosswalk.i18n import normalize_lang

_q = openapi.Parameter(
    "q", openapi.IN_QUERY,
    description="Free-text search over ESCO skill labels (case-insensitive contains)",
    type=openapi.TYPE_STRING)
_lang = openapi.Parameter("lang", openapi.IN_QUERY, description="Label language: en | es | pt",
                          type=openapi.TYPE_STRING)


@swagger_auto_schema(
    method="get",
    operation_id="skill_search",
    operation_summary="Search ESCO skills for candidate skill-picker autocomplete",
    manual_parameters=[_q, _lang],
    responses={200: "List of {skill_uuid, skill_label} objects matching the query"},
    tags=["Crosswalk"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def skill_search(request):
    q = request.GET.get("q", "").strip()
    lang = normalize_lang(request.GET.get("lang"))

    if lang == "en":
        qs = OccupationSkill.objects.values("skill_uuid", "skill_label").distinct()
        if q:
            qs = qs.filter(skill_label__icontains=q)
        seen, results = set(), []
        for row in qs.order_by("skill_label")[:200]:
            if row["skill_uuid"] not in seen:
                seen.add(row["skill_uuid"])
                results.append(row)
            if len(results) >= 20:
                break
        return Response(results)

    rows = SkillLabel.objects.filter(lang=lang)
    if q:
        rows = rows.filter(label__icontains=q)
    seen, results = set(), []
    for r in rows.order_by("label")[:200]:
        if r.skill_uuid not in seen:
            seen.add(r.skill_uuid)
            results.append({"skill_uuid": r.skill_uuid, "skill_label": r.label})
        if len(results) >= 20:
            break
    return Response(results)