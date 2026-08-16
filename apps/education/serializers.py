from rest_framework import serializers
from .models import (
    Institution, Course, School, TechnicalCourseUnit, TechnicalCourse,
    StandardCourseName, Municipality,
)


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ["ibge_code", "name", "state", "region"]


class InstitutionAutocompleteSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="municipality.name", read_only=True)
    state = serializers.CharField(source="municipality.state", read_only=True)

    class Meta:
        model = Institution
        fields = ["id", "inep_code", "name", "acronym", "city", "state", "admin_category"]


class SchoolAutocompleteSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="municipality.name", read_only=True)
    state = serializers.CharField(source="municipality.state", read_only=True)

    class Meta:
        model = School
        fields = ["id", "inep_code", "name", "city", "state", "is_vocational"]


class TechnicalCourseUnitAutocompleteSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="municipality.name", read_only=True)
    state = serializers.CharField(source="municipality.state", read_only=True)

    class Meta:
        model = TechnicalCourseUnit
        fields = ["id", "unit_code", "name", "city", "state"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id", "inep_course_code", "name", "degree_type", "academic_level",
            "teaching_modality", "is_free", "cine_area_general",
            "cine_area_specific", "cine_area_detailed",
        ]


class InstitutionDetailSerializer(serializers.ModelSerializer):
    municipality = MunicipalitySerializer(read_only=True)
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Institution
        fields = [
            "id", "inep_code", "name", "acronym", "maintainer_name",
            "academic_org_type", "network_type", "admin_category",
            "address", "neighborhood", "zip_code", "municipality",
            "website", "email", "phone", "career_center_url",
            "international_office_url", "courses",
        ]


class TechnicalCourseSerializer(serializers.ModelSerializer):
    standard_course_name = serializers.CharField(source="standard_course.course_name", read_only=True)

    class Meta:
        model = TechnicalCourse
        fields = [
            "id", "course_code", "course_name", "subtype", "technological_axis",
            "modality", "workload_hours", "is_active", "standard_course_name",
        ]


class TechnicalCourseUnitDetailSerializer(serializers.ModelSerializer):
    municipality = MunicipalitySerializer(read_only=True)
    courses = TechnicalCourseSerializer(many=True, read_only=True)

    class Meta:
        model = TechnicalCourseUnit
        fields = [
            "id", "unit_code", "name", "teaching_system", "school_type",
            "admin_dependency", "street", "number", "neighborhood",
            "zip_code", "municipality", "email", "phone", "courses",
        ]


class StandardCourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandardCourseName
        fields = ["id", "course_name", "technological_axis", "technological_area", "min_workload_hours"]