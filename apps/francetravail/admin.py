from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import JobOffer, TranslationCache


@admin.register(JobOffer)
class JobOfferAdmin(ModelAdmin):
    list_display = ("title", "company_name", "location", "department",
                    "rome_code", "contract_type", "is_active", "last_seen")
    list_filter = ("is_active", "department", "contract_type", "source")
    search_fields = ("title", "company_name", "source_id", "rome_code")
    readonly_fields = ("first_seen", "last_seen")
    ordering = ["-last_seen"]


@admin.register(TranslationCache)
class TranslationCacheAdmin(ModelAdmin):
    list_display = ("content_hash", "target_lang", "created_at")
    list_filter = ("target_lang",)
    search_fields = ("content_hash",)
    readonly_fields = ("content_hash", "target_lang", "translated", "created_at")