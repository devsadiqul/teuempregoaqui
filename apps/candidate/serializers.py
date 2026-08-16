from django.db import transaction
from rest_framework import serializers
from apps.education.models import Institution
from . import resolutions
from .models import (
    CandidateProfile, Education, WorkExperience,
    CandidateLanguage, CandidateCertification, CandidateSkill,
    PracticeCredential,
)

CEFR = ["A1", "A2", "B1", "B2", "C1", "C2", "native"]


class EducationSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), required=False, allow_null=True
    )
    institution_name = serializers.CharField(
        source="institution.name", read_only=True
    )

    class Meta:
        model = Education
        exclude = ("profile",)


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        exclude = ("profile",)


class CandidateLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateLanguage
        exclude = ("profile",)


class CandidateCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateCertification
        exclude = ("profile",)


class CandidateSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSkill
        exclude = ("profile",)

    def validate_skill_uuid(self, value):
        if value:
            from apps.crosswalk.models import OccupationSkill
            if not OccupationSkill.objects.filter(skill_uuid=value).exists():
                raise serializers.ValidationError("Unknown ESCO skill UUID.")
        return value


class PracticeCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeCredential
        exclude = ("profile",)


NESTED = {
    "education": (EducationSerializer, Education),
    "experiences": (WorkExperienceSerializer, WorkExperience),
    "languages": (CandidateLanguageSerializer, CandidateLanguage),
    "certifications": (CandidateCertificationSerializer, CandidateCertification),
    "skills": (CandidateSkillSerializer, CandidateSkill),
    "practice_credentials": (PracticeCredentialSerializer, PracticeCredential),
}


class CandidateProfileSerializer(serializers.ModelSerializer):
    education = EducationSerializer(many=True, required=False)
    experiences = WorkExperienceSerializer(many=True, required=False)
    languages = CandidateLanguageSerializer(many=True, required=False)
    certifications = CandidateCertificationSerializer(many=True, required=False)
    skills = CandidateSkillSerializer(many=True, required=False)
    practice_credentials = PracticeCredentialSerializer(many=True, required=False)

    class Meta:
        model = CandidateProfile
        fields = "__all__"
        read_only_fields = ("user_id", "session_key", "expires_at",
                            "created_at", "updated_at")

    def validate(self, attrs):
        mode = attrs.get("mode", getattr(self.instance, "mode", CandidateProfile.Mode.PRIVATE))
        if mode == CandidateProfile.Mode.ACCOUNT and not attrs.get("consent_given", False):
            raise serializers.ValidationError(
                {"consent_given": "Explicit consent is required for Personal Account Mode."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        children = {k: validated_data.pop(k, []) for k in NESTED}
        profile = CandidateProfile.objects.create(**validated_data)
        for key, rows in children.items():
            _, model = NESTED[key]
            model.objects.bulk_create([model(profile=profile, **row) for row in rows])
        return profile

    @transaction.atomic
    def update(self, instance, validated_data):
        children = {k: validated_data.pop(k, None) for k in NESTED}
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        for key, rows in children.items():
            if rows is None:
                continue
            _, model = NESTED[key]
            getattr(instance, key).all().delete()
            model.objects.bulk_create([model(profile=instance, **row) for row in rows])
        return instance


class MatchRequestSerializer(serializers.Serializer):
    profile_id = serializers.IntegerField()
    esco_uuid = serializers.UUIDField(required=False)
    rome_appellation_id = serializers.CharField(required=False)
    required_language = serializers.CharField(required=False, allow_null=True)
    required_language_level = serializers.ChoiceField(choices=CEFR, required=False, allow_null=True)
    local_language = serializers.ChoiceField(
        choices=["none", "desirable", "required"], default="none")
    experience_relevance = serializers.ChoiceField(
        choices=["directly_related", "partially_related", "different"],
        default="directly_related")
    field_relevance = serializers.ChoiceField(
        choices=["related", "partial", "unrelated"], default="related")

    def validate(self, attrs):
        if not attrs.get("esco_uuid") and not attrs.get("rome_appellation_id"):
            raise serializers.ValidationError(
                "Provide either esco_uuid or rome_appellation_id.")
        return attrs


class HowToSolveRequestSerializer(serializers.Serializer):
    gap_type = serializers.ChoiceField(choices=resolutions.VALID_GAP_TYPES, required=False)
    target_country = serializers.CharField(required=False)
    context = serializers.DictField(required=False, default=dict)
    current_score = serializers.FloatField(required=False, allow_null=True)
    gain = serializers.FloatField(required=False, default=0.0)
    profile_id = serializers.IntegerField(required=False)
    esco_uuid = serializers.UUIDField(required=False)
    rome_appellation_id = serializers.CharField(required=False)
    required_language = serializers.CharField(required=False, allow_null=True)
    required_language_level = serializers.ChoiceField(choices=CEFR, required=False, allow_null=True)
    local_language = serializers.ChoiceField(
        choices=["none", "desirable", "required"], required=False, default="none")
    lang = serializers.ChoiceField(
        choices=["en", "es", "pt"], required=False, default="en",
        help_text="Response language for cards and labels.")

    def validate(self, attrs):
        if not attrs.get("gap_type") and not attrs.get("profile_id"):
            raise serializers.ValidationError(
                "Provide gap_type (single gap) or profile_id (full report).")
        if attrs.get("gap_type") and not attrs.get("target_country"):
            raise serializers.ValidationError(
                {"target_country": "Required when gap_type is given."})
        return attrs