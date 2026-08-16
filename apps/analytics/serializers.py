from rest_framework import serializers


# Create your serializers here.
class DashboardSummarySerializer(serializers.Serializer):
    total_news          = serializers.IntegerField()
    total_articles      = serializers.IntegerField()
    total_jobs          = serializers.IntegerField()
    avg_feedback_rating = serializers.FloatField()


class FeedbackSummarySerializer(serializers.Serializer):
    total_feedbacks     = serializers.IntegerField()
    pending_feedbacks   = serializers.IntegerField()
    resolved_feedbacks  = serializers.IntegerField()
    avg_feedback_rating = serializers.FloatField()