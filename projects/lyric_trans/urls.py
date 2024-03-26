from django.urls import path
from . import views

app_name = "lyric_trans"
urlpatterns = [
    path("", views.index, name="index"),
]