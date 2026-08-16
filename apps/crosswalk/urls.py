from django.urls import path, register_converter
from apps.crosswalk.converters import EscoUuidConverter
from apps.crosswalk.views.skill_search import skill_search
from .views.occupation_list import occupation_list
from .views.occupation_detail import occupation_detail
from .views.occupation_skills import occupation_skills

register_converter(EscoUuidConverter, "esco")


urlpatterns = [
    path("occupations/", occupation_list, name="occupation-list"),
    path("occupations/<esco:esco_uuid>/", occupation_detail, name="occupation-detail"),
    path("occupations/<esco:esco_uuid>/skills/", occupation_skills, name="occupation-skills"),
    path("skills/", skill_search, name="skill-search"),
]