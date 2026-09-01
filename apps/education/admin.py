from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    Municipality, Institution, Course, School,
    TechnicalCourseUnit, TechnicalCourse, StandardCourseName,
)


@admin.register(Municipality)
class MunicipalityAdmin(ModelAdmin):
    list_display = ("name", "state", "ibge_code", "region")
    list_filter = ("state",)
    search_fields = ("name", "ibge_code")


class CourseInline(TabularInline):
    model = Course
    extra = 0
    fields = ("name", "degree_type", "academic_level", "teaching_modality", "is_free")


@admin.register(Institution)
class InstitutionAdmin(ModelAdmin):
    list_display = ("name", "acronym", "municipality", "admin_category", "network_type", "census_year")
    list_filter = ("admin_category", "network_type", "is_community", "is_confessional", "census_year")
    search_fields = ("name", "acronym", "inep_code", "maintainer_name")
    autocomplete_fields = ("municipality",)
    inlines = [CourseInline]


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ("name", "institution", "degree_type", "academic_level", "teaching_modality", "is_free")
    list_filter = ("degree_type", "academic_level", "teaching_modality", "is_free")
    search_fields = ("name", "inep_course_code", "institution__name")
    autocomplete_fields = ("institution", "municipality")


@admin.register(School)
class SchoolAdmin(ModelAdmin):
    list_display = ("name", "municipality", "is_vocational", "dependency_type", "operating_status")
    list_filter = ("is_vocational", "dependency_type", "operating_status", "location_type")
    search_fields = ("name", "inep_code")
    autocomplete_fields = ("municipality", "run_by_institution")


class TechnicalCourseInline(TabularInline):
    model = TechnicalCourse
    extra = 0
    fields = ("course_name", "subtype", "modality", "workload_hours", "is_active", "standard_course")


@admin.register(TechnicalCourseUnit)
class TechnicalCourseUnitAdmin(ModelAdmin):
    list_display = ("name", "municipality", "teaching_system", "admin_dependency")
    list_filter = ("teaching_system", "school_type", "admin_dependency")
    search_fields = ("name", "unit_code")
    autocomplete_fields = ("municipality", "linked_institution", "linked_school")
    inlines = [TechnicalCourseInline]


@admin.register(TechnicalCourse)
class TechnicalCourseAdmin(ModelAdmin):
    list_display = ("course_name", "unit", "modality", "workload_hours", "is_active")
    list_filter = ("modality", "is_active", "technological_axis")
    search_fields = ("course_name", "course_code", "unit__name")
    autocomplete_fields = ("unit", "standard_course")


@admin.register(StandardCourseName)
class StandardCourseNameAdmin(ModelAdmin):
    list_display = ("course_name", "technological_axis", "technological_area", "min_workload_hours")
    list_filter = ("technological_axis",)
    search_fields = ("course_name",)