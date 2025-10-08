from django.urls import path
from . import views

app_name = 'bond_checker'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('list/', views.document_list, name='document_list'),
]
