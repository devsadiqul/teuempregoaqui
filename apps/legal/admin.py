from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Legal


@admin.register(Legal)
class LegalAdmin(ModelAdmin):
    list_display  = ['document_type', 'title', 'version', 'is_active', 'created_at', 'updated_at']
    list_filter   = ['document_type', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['version', 'created_at', 'updated_at']
    ordering      = ['-created_at']