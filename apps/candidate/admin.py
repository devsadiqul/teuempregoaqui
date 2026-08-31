from django.contrib import admin
from .models import (CandidateProfile, Education, WorkExperience,
                     CandidateLanguage, CandidateCertification, CandidateSkill,
                     PracticeCredential, Nationality)


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ("country_of_birth", "current_nationality", "country_of_residence", "target_country")


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    autocomplete_fields = ("country",)


@admin.register(PracticeCredential)
class PracticeCredentialAdmin(admin.ModelAdmin):
    autocomplete_fields = ("country",)


admin.site.register(CandidateLanguage)
admin.site.register(CandidateCertification)
admin.site.register(CandidateSkill)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    autocomplete_fields = ("institution", "country_of_qualification")


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ("location", "demonym", "demonym_es", "demonym_pt")
    search_fields = ("location__name", "demonym", "demonym_es", "demonym_pt")
    autocomplete_fields = ("location",)