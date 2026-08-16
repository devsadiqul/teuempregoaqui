from django.urls import path
from .views import (
    institution_list, institution_detail,
    school_list,
    technical_course_unit_list, technical_course_unit_detail,
    standard_course_name_list,
)

urlpatterns = [
    path("institutions/", institution_list, name="institution-list"),
    path("institutions/<int:pk>/", institution_detail, name="institution-detail"),

    path("schools/", school_list, name="school-list"),

    path("technical-units/", technical_course_unit_list, name="technical-unit-list"),
    path("technical-units/<int:pk>/", technical_course_unit_detail, name="technical-unit-detail"),

    path("technical-courses/standard-names/", standard_course_name_list, name="standard-course-name-list"),
]