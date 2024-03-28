from django.urls import path
from . import views
from .views import upload_audio
from .views import delete_audio

app_name = "whispar"
urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', upload_audio, name='upload_audio'),
    path('delete-audio/', views.delete_audio, name='delete_audio'),
]