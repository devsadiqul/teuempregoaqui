from django.contrib import admin
from .models import EscoOccupation, OccupationSkill, RomeEscoMapping


admin.site.register(EscoOccupation)
admin.site.register(OccupationSkill)
admin.site.register(RomeEscoMapping)
