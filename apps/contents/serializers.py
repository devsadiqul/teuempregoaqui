from rest_framework import serializers
from .models import (
    NewsCategory, News,
    ArticleCategory, Article,
    OfficialSource, FAQ, Feedback,
)


# Write your serializers here.
class NewsCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = NewsCategory
        fields = ['id', 'name', 'name_es', 'name_pt', 'slug', 'order', 'is_active']
        extra_kwargs = {
            'name_es': {'write_only': True},
            'name_pt': {'write_only': True},
        }

    def get_name(self, obj):
        request = self.context.get('request')
        lang = (request.query_params.get('lang') or 'en') if request else 'en'
        return obj.localized_name(lang)


class NewsSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=NewsCategory.objects.all(), source='category',
        write_only=True, required=False, allow_null=True)
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'category', 'category_id', 'author_id', 'author_name', 'author_avatar_url',
            'title', 'title_es', 'title_pt', 'slug', 'location', 'thumbnail', 'content', 'content_es', 'content_pt',
            'read_time', 'is_featured', 'is_published', 'views_count',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'title_es': {'write_only': True}, 'title_pt': {'write_only': True},
            'content_es': {'write_only': True}, 'content_pt': {'write_only': True},
        }

    def _lang(self):
        request = self.context.get('request')
        return (request.query_params.get('lang') or 'en') if request else 'en'

    def get_title(self, obj):
        return obj.localized_title(self._lang())

    def get_content(self, obj):
        return obj.localized_content(self._lang())

class ArticleCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ArticleCategory
        fields = ['id', 'name', 'name_es', 'name_pt', 'slug', 'order', 'is_active']
        extra_kwargs = {
            'name_es': {'write_only': True},
            'name_pt': {'write_only': True},
        }

    def get_name(self, obj):
        request = self.context.get('request')
        lang = (request.query_params.get('lang') or 'en') if request else 'en'
        return obj.localized_name(lang)


class ArticleSerializer(serializers.ModelSerializer):
    category = ArticleCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ArticleCategory.objects.all(), source='category',
        write_only=True, required=False, allow_null=True)
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'category', 'category_id', 'title', 'title_es', 'title_pt', 'slug', 'content', 'content_es', 'content_pt',
            'read_time', 'official_source_label', 'official_source_url',
            'is_published', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'title_es': {'write_only': True}, 'title_pt': {'write_only': True},
            'content_es': {'write_only': True}, 'content_pt': {'write_only': True},
        }

    def _lang(self):
        request = self.context.get('request')
        return (request.query_params.get('lang') or 'en') if request else 'en'

    def get_title(self, obj):
        return obj.localized_title(self._lang())

    def get_content(self, obj):
        return obj.localized_content(self._lang())

class OfficialSourceNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficialSource
        fields = ['id', 'name']


class OfficialSourceSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = OfficialSource
        fields = [
            'id', 'name', 'description', 'description_es', 'description_pt',
            'url', 'icon', 'country', 'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'description_es': {'write_only': True},
            'description_pt': {'write_only': True},
        }

    def get_description(self, obj):
        request = self.context.get('request')
        lang = 'en'
        if request is not None:
            lang = (request.query_params.get('lang') or 'en')
        return obj.localized_description(lang)


class FAQSerializer(serializers.ModelSerializer):
    language = serializers.CharField(write_only=True, required=False, default='en')

    class Meta:
        model = FAQ
        fields = ['id', 'language', 'question', 'answer', 'order', 'is_active']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user_id', 'rating', 'category', 'message', 'is_resolved', 'created_at']
        read_only_fields = ['id', 'user_id', 'is_resolved', 'created_at']