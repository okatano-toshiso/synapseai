from django.urls import path
from . import views

app_name = "win5"
urlpatterns = [
    path("", views.index, name="index"),
]