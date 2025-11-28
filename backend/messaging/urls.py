from django.urls import path
from .views import (
    CreateConversationAPIView,
    ChatListAPIView
)

urlpatterns = [
    path('create/', CreateConversationAPIView.as_view(), name='Create Conversation'),
    path('conversation-list/', ChatListAPIView.as_view(), name='Message List'),
]
