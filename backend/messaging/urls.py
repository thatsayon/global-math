from django.urls import path
from .views import (
    ConversationMessagesAPIView,
    ChatListAPIView
)

urlpatterns = [
    path('create/', CreateConversationAPIView.as_view(), name='Create Conversation'),
    path('conversation-list/', ConversationMessagesAPIView.as_view(), name='Message List'),
]
