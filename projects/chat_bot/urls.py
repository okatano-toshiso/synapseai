from django.urls import path
from . import views
urlpatterns = [
    path('ask/', views.ask, name='ask'),
    path('chat/', views.chat_view, name='chat_view'),
]