from django.urls import path
from . import views
from .views import delete_file

app_name = "tts"
urlpatterns = [
    path("", views.index, name="index"),
    path('delete-file', delete_file, name='delete-file'),
]