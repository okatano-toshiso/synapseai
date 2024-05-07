from django.urls import path
from . import views

app_name = "aphorism"
urlpatterns = [
    path("", views.index, name="index"),
]