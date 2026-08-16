from django.contrib import admin
from .models import (CandidateProfile, Education, WorkExperience,
                     CandidateLanguage, CandidateCertification, CandidateSkill)

admin.site.register(CandidateProfile)
admin.site.register(WorkExperience)
admin.site.register(CandidateLanguage)
admin.site.register(CandidateCertification)
admin.site.register(CandidateSkill)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    autocomplete_fields = ("institution",)