from django.urls import path
from . import views

app_name = "jra_scraping"
urlpatterns = [
    path("", views.index, name="index"),
    path('download/<str:file_name>/', views.download_file, name='download_file'),
]