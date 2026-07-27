from django.urls import path
from . import views

app_name = "study"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("study/", views.study, name="study"),
    path("review/<int:card_id>/", views.review, name="review"),
    path("reset/", views.reset_progress, name="reset"),
    path("history/", views.history_list, name="history"),
    path("stats/", views.stats_overview, name="stats"),
    path("stats/<str:chapter>/", views.stats_detail, name="stats_detail"),
    path("cards/", views.card_list, name="card_list"),
    path("cards/new/", views.card_create, name="card_create"),
    path("cards/<int:card_id>/edit/", views.card_update, name="card_update"),
    path("cards/<int:card_id>/delete/", views.card_delete, name="card_delete"),
]
