from django.urls import path
from . import views


# Write your URL patterns here.
urlpatterns = [
    # News Categories URLs
    path('news-categories/', views.get_categories, name='news-category-list'),
    path('news-categories/create/', views.create_category, name='news-category-create'),
    path('news-categories/<int:pk>/update/', views.update_category, name='news-category-update'),
    path('news-categories/<int:pk>/delete/', views.delete_category, name='news-category-delete'),

    # News
    path('news/', views.get_all_news, name='news-list'),
    path('news/create/', views.create_news, name='news-create'),
    path('news/<slug:slug>/', views.get_news_detail, name='news-detail'),
    path('news/<slug:slug>/update/', views.update_news, name='news-update'),
    path('news/<slug:slug>/delete/', views.delete_news, name='news-delete'),

    # Article Categories
    path('article-categories/', views.get_article_category_list, name='article-category-list'),
    path('article-categories/create/', views.create_article_category, name='article-category-create'),
    path('article-categories/<slug:slug>/', views.get_article_category, name='article-category-detail'),
    path('article-categories/<slug:slug>/update/', views.update_article_category, name='article-category-update'),
    path('article-categories/<slug:slug>/delete/', views.delete_article_category, name='article-category-delete'),

    # Articles
    path('articles/', views.get_article_list, name='article-list'),
    path('articles/create/', views.create_article, name='article-create'),
    path('articles/<slug:slug>/', views.get_article, name='article-detail'),
    path('articles/<slug:slug>/update/', views.update_article, name='article-update'),
    path('articles/<slug:slug>/delete/', views.delete_article, name='article-delete'),

    # Official Sources
    path('official-sources/names/', views.official_source_names, name='official-source-names'),
    path('official-sources/', views.get_official_source_list, name='official-source-list'),
    path('official-sources/create/', views.create_official_source, name='official-source-create'),
    path('official-sources/<int:pk>/', views.get_official_source, name='official-source-detail'),
    path('official-sources/<int:pk>/update/', views.update_official_source, name='official-source-update'),
    path('official-sources/<int:pk>/delete/', views.delete_official_source, name='official-source-delete'),

    # FAQ
    path('faqs/', views.get_faq_list, name='faq-list'),
    path('faqs/create/', views.create_faq, name='faq-create'),
    path('faqs/<int:pk>/', views.get_faq, name='faq-detail'),
    path('faqs/<int:pk>/update/', views.update_faq, name='faq-update'),
    path('faqs/<int:pk>/delete/', views.delete_faq, name='faq-delete'),

    # Feedback
    path('feedbacks/', views.get_feedback_list, name='feedback-list'),
    path('feedbacks/create/', views.create_feedback, name='feedback-create'),
    path('feedbacks/<int:pk>/', views.get_feedback, name='feedback-detail'),
    path('feedbacks/<int:pk>/resolve/', views.resolve_feedback, name='feedback-resolve'),
    path('feedbacks/<int:pk>/delete/', views.delete_feedback, name='feedback-delete'),
]