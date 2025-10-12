from django.urls import path
from . import views

# urlpatterns = [
#     path('topic/', views.topic, name='topic'),
# # +    # path('discussion/', views.discussion, name='discussion'),
#     # path('discussion/', views.discussion, name='chat_interaction_discussion'),
#     path('discussion/', views.chat_interaction_discussion, name='results'),

# ]
urlpatterns = [
    path('topic/', views.topic, name='chat_interaction_topic'),
    path('discussion/', views.chat_interaction_discussion, name='chat_interaction_discussion'),
    path('reset/', views.reset_chat, name='reset_chat'),
]