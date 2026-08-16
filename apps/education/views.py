from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.education.models import (
    Institution, School, TechnicalCourseUnit, StandardCourseName,
)
from apps.education.serializers import (
    InstitutionAutocompleteSerializer, InstitutionDetailSerializer,
    SchoolAutocompleteSerializer,
    TechnicalCourseUnitAutocompleteSerializer, TechnicalCourseUnitDetailSerializer,
    StandardCourseNameSerializer,
)

# ── Shared query params ──────────────────────────────────────────────────────

_q = openapi.Parameter("q", openapi.IN_QUERY, description="Search text (name / acronym)",
                       type=openapi.TYPE_STRING)
_state = openapi.Parameter("state", openapi.IN_QUERY, description="Brazilian state code, e.g. SP",
                           type=openapi.TYPE_STRING)
_city = openapi.Parameter("city", openapi.IN_QUERY, description="Municipality name",
                          type=openapi.TYPE_STRING)
_limit = openapi.Parameter("limit", openapi.IN_QUERY, description="Max results (default 20, max 100)",
                           type=openapi.TYPE_INTEGER)


def _get_limit(request, default=20, cap=100):
    try:
        return min(int(request.query_params.get("limit", default)), cap)
    except ValueError:
        return default


# ── Institutions (universities / colleges) ───────────────────────────────────

_org_type = openapi.Parameter("admin_category", openapi.IN_QUERY,
                              description="Administrative category (public/private)",
                              type=openapi.TYPE_STRING)
_course = openapi.Parameter("course", openapi.IN_QUERY, description="Filter by course name",
                            type=openapi.TYPE_STRING)


@swagger_auto_schema(
    method="get",
    operation_id="institutions_search",
    operation_summary="Search higher education institutions (universities/colleges)",
    manual_parameters=[_q, _state, _city, _org_type, _course, _limit],
    responses={200: InstitutionAutocompleteSerializer(many=True)},
    tags=["Education"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def institution_list(request):
    qs = Institution.objects.select_related("municipality").all()

    q = request.query_params.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(acronym__icontains=q)

    state = request.query_params.get("state", "").strip()
    if state:
        qs = qs.filter(municipality__state__iexact=state)

    city = request.query_params.get("city", "").strip()
    if city:
        qs = qs.filter(municipality__name__icontains=city)

    admin_category = request.query_params.get("admin_category", "").strip()
    if admin_category:
        qs = qs.filter(admin_category__icontains=admin_category)

    course = request.query_params.get("course", "").strip()
    if course:
        qs = qs.filter(courses__name__icontains=course)

    results = qs.distinct()[:_get_limit(request)]
    data = InstitutionAutocompleteSerializer(results, many=True).data
    return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_id="institution_detail",
    operation_summary="Retrieve one institution with its courses",
    responses={200: InstitutionDetailSerializer(), 404: "Not found"},
    tags=["Education"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def institution_detail(request, pk):
    institution = get_object_or_404(
        Institution.objects.select_related("municipality").prefetch_related("courses"),
        pk=pk,
    )
    return Response(InstitutionDetailSerializer(institution).data, status=status.HTTP_200_OK)


# ── Schools (K-12 / basic education) ─────────────────────────────────────────

_vocational = openapi.Parameter("is_vocational", openapi.IN_QUERY,
                                description="Filter to vocational schools only (true/false)",
                                type=openapi.TYPE_BOOLEAN)


@swagger_auto_schema(
    method="get",
    operation_id="schools_search",
    operation_summary="Search K-12 / basic education schools",
    manual_parameters=[_q, _state, _city, _vocational, _limit],
    responses={200: SchoolAutocompleteSerializer(many=True)},
    tags=["Education"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def school_list(request):
    qs = School.objects.select_related("municipality").all()

    q = request.query_params.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)

    state = request.query_params.get("state", "").strip()
    if state:
        qs = qs.filter(municipality__state__iexact=state)

    city = request.query_params.get("city", "").strip()
    if city:
        qs = qs.filter(municipality__name__icontains=city)

    is_vocational = request.query_params.get("is_vocational")
    if is_vocational is not None:
        qs = qs.filter(is_vocational=is_vocational.strip().lower() in ("true", "1", "yes"))

    results = qs.distinct()[:_get_limit(request)]
    data = SchoolAutocompleteSerializer(results, many=True).data
    return Response(data, status=status.HTTP_200_OK)


# ── Technical course units (SISTEC) ──────────────────────────────────────────

@swagger_auto_schema(
    method="get",
    operation_id="technical_units_search",
    operation_summary="Search SISTEC technical/vocational course units",
    manual_parameters=[_q, _state, _city, _course, _limit],
    responses={200: TechnicalCourseUnitAutocompleteSerializer(many=True)},
    tags=["Education"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def technical_course_unit_list(request):
    qs = TechnicalCourseUnit.objects.select_related("municipality").all()

    q = request.query_params.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)

    state = request.query_params.get("state", "").strip()
    if state:
        qs = qs.filter(municipality__state__iexact=state)

    city = request.query_params.get("city", "").strip()
    if city:
        qs = qs.filter(municipality__name__icontains=city)

    course = request.query_params.get("course", "").strip()
    if course:
        qs = qs.filter(courses__course_name__icontains=course)

    results = qs.distinct()[:_get_limit(request)]
    data = TechnicalCourseUnitAutocompleteSerializer(results, many=True).data
    return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_id="technical_unit_detail",
    operation_summary="Retrieve one technical course unit with its courses",
    responses={200: TechnicalCourseUnitDetailSerializer(), 404: "Not found"},
    tags=["Education"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def technical_course_unit_detail(request, pk):
    unit = get_object_or_404(
        TechnicalCourseUnit.objects.select_related("municipality").prefetch_related("courses"),
        pk=pk,
    )
    return Response(TechnicalCourseUnitDetailSerializer(unit).data, status=status.HTTP_200_OK)


# ── Standard course names (CNCT catalog — for normalized dropdowns) ──────────

@swagger_auto_schema(
    method="get",
    operation_id="standard_course_names_search",
    operation_summary="Search the normalized CNCT technical course catalog",
    manual_parameters=[_q, _limit],
    responses={200: StandardCourseNameSerializer(many=True)},
    tags=["Education"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def standard_course_name_list(request):
    qs = StandardCourseName.objects.all()

    q = request.query_params.get("q", "").strip()
    if q:
        qs = qs.filter(course_name__icontains=q)

    results = qs[:_get_limit(request)]
    data = StandardCourseNameSerializer(results, many=True).data
    return Response(data, status=status.HTTP_200_OK)