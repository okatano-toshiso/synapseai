from django.urls import path
from . import views

app_name = 'bond_checker'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('documents/', views.document_list, name='document_list'),
    path('test-gpt4o/', views.test_gpt4o, name='test_gpt4o'),
    path('clear-all/', views.clear_all, name='clear_all'),
]
