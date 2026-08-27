from django.urls import path
from .views.profile_collection import profile_collection
from .views.profile_detail import profile_detail
from .views.profile_review import profile_review
from .views.match import match
from .views.how_to_solve import how_to_solve


urlpatterns = [
    path("candidates/", profile_collection, name="candidate-collection"),
    path("candidates/<int:pk>/", profile_detail, name="candidate-detail"),
    path("candidates/<int:pk>/review/", profile_review, name="candidate-review"),
    path("match/", match, name="match"),
    path("how-to-solve/", how_to_solve, name="how-to-solve"),
]