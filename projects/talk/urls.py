from django.urls import path
from . import views
from .views import upload_audio
from .views import delete_file

app_name = "talk"
urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', upload_audio, name='upload_audio'),
    path('delete-file', delete_file, name='delete-file'),
]