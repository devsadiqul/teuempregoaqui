from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import EscoOccupation, OccupationSkill, RomeEscoMapping


@admin.register(EscoOccupation)
class EscoOccupationAdmin(ModelAdmin):
    list_display = ("code", "label", "isco_group", "regulated")
    list_filter = ("regulated", "isco_group")
    search_fields = ("code", "label", "label_es", "label_pt")


@admin.register(OccupationSkill)
class OccupationSkillAdmin(ModelAdmin):
    list_display = ("occupation", "skill_label", "relation")
    list_filter = ("relation",)
    search_fields = ("skill_label", "occupation__label")
    autocomplete_fields = ("occupation",)


@admin.register(RomeEscoMapping)
class RomeEscoMappingAdmin(ModelAdmin):
    list_display = ("rome_appellation_id", "rome_label", "occupation")
    search_fields = ("rome_appellation_id", "rome_label")
    autocomplete_fields = ("occupation",)