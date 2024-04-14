from django.urls import path
from . import views

app_name = "response_mail"
urlpatterns = [
    path("", views.index, name="index"),
]