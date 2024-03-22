from django.urls import path
from . import views

app_name = "generate_image"
urlpatterns = [
    path("", views.index, name="index"),
]