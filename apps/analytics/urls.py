from django.urls import path
from . import views


# Write your URL patterns here.
urlpatterns = [
    path('summary/', views.dashboard_summary, name='dashboard-summary'),
    path('feedback/summary/', views.feedback_summary, name='feedback-summary'),
    path('job-postings/', views.job_postings, name='job-postings'),
    path('recently-added-jobs/', views.recently_added_jobs, name='recently-added-jobs'),
    path('latest-published-news/', views.latest_published_news, name='latest-published-news'),
]