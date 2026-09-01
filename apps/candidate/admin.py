from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (CandidateProfile, Education, WorkExperience,
                     CandidateLanguage, CandidateCertification, CandidateSkill,
                     PracticeCredential, Nationality)


@admin.register(CandidateProfile)
class CandidateProfileAdmin(ModelAdmin):
    autocomplete_fields = ("country_of_birth", "current_nationality", "country_of_residence", "target_country")
    list_display = ("full_name", "email", "mode", "target_country", "is_expired", "created_at")
    list_filter = ("mode", "work_authorization", "immigration_status")
    search_fields = ("full_name", "email", "user_id", "session_key")
    readonly_fields = ("created_at", "updated_at", "expires_at")


@admin.register(WorkExperience)
class WorkExperienceAdmin(ModelAdmin):
    autocomplete_fields = ("country",)
    list_display = ("position", "employer", "profile", "start_date", "end_date", "is_current")
    search_fields = ("position", "employer", "profile__full_name")


@admin.register(PracticeCredential)
class PracticeCredentialAdmin(ModelAdmin):
    autocomplete_fields = ("country",)
    list_display = ("profile", "country", "recognition_status", "regulated_profession_status")
    list_filter = ("recognition_status", "regulated_profession_status")


@admin.register(CandidateLanguage)
class CandidateLanguageAdmin(ModelAdmin):
    list_display = ("profile", "language", "level", "source")
    list_filter = ("source",)
    search_fields = ("language", "profile__full_name")


@admin.register(CandidateCertification)
class CandidateCertificationAdmin(ModelAdmin):
    list_display = ("name", "profile")
    search_fields = ("name", "profile__full_name")


@admin.register(CandidateSkill)
class CandidateSkillAdmin(ModelAdmin):
    list_display = ("name", "profile", "proficiency", "source")
    list_filter = ("source",)
    search_fields = ("name", "profile__full_name", "skill_uuid")


@admin.register(Education)
class EducationAdmin(ModelAdmin):
    autocomplete_fields = ("institution", "country_of_qualification")
    list_display = ("profile", "eqf_level", "field_of_study", "degree_recognized")
    list_filter = ("eqf_level", "field_of_study", "degree_recognized", "regulated_profession")


@admin.register(Nationality)
class NationalityAdmin(ModelAdmin):
    list_display = ("location", "demonym", "demonym_es", "demonym_pt")
    search_fields = ("location__name", "demonym", "demonym_es", "demonym_pt")
    autocomplete_fields = ("location",)