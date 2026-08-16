from django.contrib import admin
from .models import (
    NewsCategory, News,
    ArticleCategory, Article,
    OfficialSource, FAQ, Feedback,
)


# Register your models here.
@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'id']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author_name', 'location', 'read_time', 'is_featured', 'is_published', 'views_count', 'created_at')
    list_editable = ('is_featured', 'is_published')
    list_filter = ('category', 'is_featured', 'is_published', 'location')
    search_fields = ('title', 'author_name', 'content')
    readonly_fields = ('slug', 'read_time', 'views_count', 'created_at', 'updated_at')
    ordering = ['-created_at']


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'id']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'read_time', 'official_source_label', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'content', 'official_source_label')
    readonly_fields = ('slug', 'read_time', 'created_at', 'updated_at')
    ordering = ['-created_at']


@admin.register(OfficialSource)
class OfficialSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'country')
    list_filter = ('country', 'is_active')
    ordering = ['order', 'id']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')
    ordering = ['order', 'id']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('category', 'rating', 'user_id', 'is_resolved', 'created_at')
    list_editable = ('is_resolved',)
    list_filter = ('category', 'rating', 'is_resolved')
    search_fields = ('user_id', 'message')
    readonly_fields = ('user_id', 'rating', 'category', 'message', 'created_at', 'updated_at')
    ordering = ['-created_at']