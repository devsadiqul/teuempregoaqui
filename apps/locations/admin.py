from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "location_type", "country_code", "parent", "depth", "is_active"]
    list_filter = ["country_code", "location_type", "is_active"]
    search_fields = ["name", "local_name"]
    ordering = ["country_code", "depth", "name"]
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
