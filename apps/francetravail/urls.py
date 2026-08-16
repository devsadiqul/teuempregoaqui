from django.urls import path
from .views.recommended_jobs import recommended_jobs
from .views.offer_list import offer_list
from .views.offer_sync import offer_sync
from .views.offer_match import offer_match


urlpatterns = [
    path("offers/", offer_list, name="offer-list"),
    path("offers/sync/", offer_sync, name="offer-sync"),
    path("offers/<str:source_id>/match/", offer_match, name="offer-match"),
    path("recommend/", recommended_jobs, name="recommend"),
]
