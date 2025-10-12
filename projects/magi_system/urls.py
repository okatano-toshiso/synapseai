from django.urls import path
from . import views

urlpatterns = [
    path('topic/', views.topic, name='topic'),
    path('results/', views.magi_discussion, name='results'),
]