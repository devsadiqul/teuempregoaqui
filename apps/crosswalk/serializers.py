from rest_framework import serializers
from .models import EscoOccupation, OccupationSkill


class EscoOccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscoOccupation
        fields = ["esco_uuid", "code", "isco_group", "label", "regulated"]


class OccupationSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupationSkill
        fields = ["skill_uuid", "skill_label", "relation", "skill_type"]
