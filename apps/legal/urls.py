from django.urls import path
from . import views


# Write your URL patterns here.
urlpatterns = [
    path('', views.legal_upsert,  name='legal-upsert'),
    path('detail/', views.legal_detail,  name='legal-detail'),
]