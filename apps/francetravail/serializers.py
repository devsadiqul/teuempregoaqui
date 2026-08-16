from rest_framework import serializers
from .models import JobOffer


class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = [
            "id", "source", "source_id", "source_url", "title", "description",
            "rome_code", "rome_label", "appellation_label", "esco_uuid",
            "contract_type", "company_name", "location", "department",
            "salary", "posted_at", "is_active", "last_seen",
        ]


class OfferSyncRequestSerializer(serializers.Serializer):
    rome = serializers.CharField(required=False, help_text="ROME metier code, e.g. M1805")
    mots_cles = serializers.CharField(required=False, help_text="Free-text keywords")
    departement = serializers.CharField(required=False, help_text="FR department, e.g. 75")
    max_offers = serializers.IntegerField(required=False, default=150)

    def validate(self, attrs):
        if not attrs.get("rome") and not attrs.get("mots_cles"):
            raise serializers.ValidationError("Provide rome or mots_cles.")
        return attrs


class OfferMatchRequestSerializer(serializers.Serializer):
    profile_id = serializers.IntegerField()
    required_language_level = serializers.ChoiceField(
        choices=["A1", "A2", "B1", "B2", "C1", "C2"], required=False, allow_null=True)
    local_language = serializers.ChoiceField(
        choices=["none", "desirable", "required"], default="required")
    experience_relevance = serializers.ChoiceField(
        choices=["directly_related", "partially_related", "different"],
        default="directly_related")
    field_relevance = serializers.ChoiceField(
        choices=["related", "partial", "unrelated"], default="related")


class RecommendRequestSerializer(serializers.Serializer):
    profile_id = serializers.IntegerField()
    limit = serializers.IntegerField(required=False, default=20)
    min_score = serializers.FloatField(required=False, default=0.0)
    departement = serializers.CharField(required=False)
    lang = serializers.ChoiceField(choices=["en", "es", "pt"], default="en")
    local_language = serializers.ChoiceField(
        choices=["none", "desirable", "required"], default="required")
    experience_relevance = serializers.ChoiceField(
        choices=["directly_related", "partially_related", "different"],
        default="directly_related")
    field_relevance = serializers.ChoiceField(
        choices=["related", "partial", "unrelated"], default="related")