from django.urls import path
from . import views

app_name = "jra"
urlpatterns = [
    path("", views.index, name="index"),
]