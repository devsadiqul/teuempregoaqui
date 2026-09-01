from rest_framework import serializers


class EvolutionActionSchema(serializers.Serializer):
    gap_type = serializers.CharField()
    action = serializers.CharField()
    gain = serializers.FloatField()
    evidence_status = serializers.CharField(required=False)
    detail = serializers.ListField(child=serializers.CharField(), required=False)
    context = serializers.DictField(required=False)


class EvolutionSchema(serializers.Serializer):
    current = serializers.FloatField()
    potential = serializers.FloatField()
    classification_potential = serializers.CharField()
    actions = EvolutionActionSchema(many=True)


class RecognitionRequirementSchema(serializers.Serializer):
    status = serializers.CharField()
    competent_authority = serializers.CharField(allow_blank=True)
    official_source_url = serializers.CharField(allow_blank=True)
    evidence_status = serializers.CharField()


class MatchTargetSchema(serializers.Serializer):
    esco_uuid = serializers.CharField()
    code = serializers.CharField()
    label = serializers.CharField()
    essential_skill_count = serializers.IntegerField()
    regulated = serializers.BooleanField()
    recognition_requirement = RecognitionRequirementSchema(allow_null=True)


class DimensionSchema(serializers.Serializer):
    """One auditable sub-score. status is one of: verified,
    declared_unverified, missing, not_compliant, not_applicable - see
    apps.candidate.scoring.Evidence."""
    score = serializers.FloatField()
    weight = serializers.FloatField()
    status = serializers.CharField()
    note = serializers.CharField(allow_blank=True)


class EligibilitySchema(serializers.Serializer):
    eligible = serializers.BooleanField()
    reason = serializers.CharField(allow_null=True)
    requirement = serializers.CharField(allow_null=True)
    evidence_status = serializers.CharField(allow_null=True)


class JobMatchScoreSchema(serializers.Serializer):
    total = serializers.FloatField()
    confidence = serializers.FloatField()
    classification = serializers.CharField()
    eligibility = EligibilitySchema()
    dimensions = serializers.DictField(child=DimensionSchema())
    matched_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())


class EmployabilityIndexSchema(serializers.Serializer):
    total = serializers.FloatField()
    confidence = serializers.FloatField()
    classification = serializers.CharField()
    dimensions = serializers.DictField(child=DimensionSchema())


class BlocksSchema(serializers.Serializer):
    """Deprecated legacy mirror of job_match_score.dimensions[*].score,
    kept only while frontend consumers migrate."""
    esco_occupational_match = serializers.FloatField()
    skills = serializers.FloatField()
    experience = serializers.FloatField()
    languages = serializers.FloatField()
    location = serializers.FloatField()
    recognition = serializers.FloatField()


class MatchResponseSchema(serializers.Serializer):
    job_match_score = JobMatchScoreSchema()
    employability_index = EmployabilityIndexSchema()
    # Legacy-compatible fields (deprecated - use job_match_score instead)
    blocks = BlocksSchema()
    total = serializers.FloatField()
    classification = serializers.CharField()
    matched_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    evolution = EvolutionSchema()
    target = MatchTargetSchema()


class HowToSolveCardSchema(serializers.Serializer):
    title = serializers.CharField()
    explanation = serializers.CharField()
    recommended_actions = serializers.ListField(child=serializers.CharField())
    estimated_timeline = serializers.CharField()
    estimated_cost = serializers.CharField()
    institution = serializers.CharField()
    official_link = serializers.CharField()
    goal = serializers.CharField()
    gap_type = serializers.CharField()
    target_country = serializers.CharField()
    priority_level = serializers.IntegerField()
    impact = serializers.CharField()
    expected_impact_points = serializers.FloatField()
    projected_compatibility = serializers.CharField(allow_null=True)
    data_disclaimer = serializers.CharField()
    missing_skills = serializers.ListField(child=serializers.CharField(), required=False)


class HowToSolveReportSchema(serializers.Serializer):
    total = serializers.FloatField()
    classification = serializers.CharField()
    potential = serializers.FloatField()
    target = MatchTargetSchema()
    how_to_solve = HowToSolveCardSchema(many=True)


class RecommendedJobSchema(serializers.Serializer):
    source_id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    company_name = serializers.CharField()
    location = serializers.CharField()
    rome_code = serializers.CharField()
    source_url = serializers.CharField()
    esco_label = serializers.CharField(allow_null=True)
    score = serializers.FloatField()
    classification = serializers.CharField()
    potential = serializers.FloatField()
    missing_skills = serializers.ListField(child=serializers.CharField())


class RecommendResponseSchema(serializers.Serializer):
    count = serializers.IntegerField()
    recommended = RecommendedJobSchema(many=True)


class OfferMetaSchema(serializers.Serializer):
    source_id = serializers.CharField()
    title = serializers.CharField()
    company = serializers.CharField()
    location = serializers.CharField()
    rome_code = serializers.CharField()
    source_url = serializers.CharField()
    esco_uuid = serializers.CharField(allow_null=True)
    esco_label = serializers.CharField(allow_null=True)
    resolved_to_esco = serializers.BooleanField()


class OfferMatchResponseSchema(MatchResponseSchema):
    offer = OfferMetaSchema()