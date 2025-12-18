from django.urls import path, include
from .views import (
    CreateConversationAPIView,
    ChatListAPIView,
    ConversationDetailView,
)

urlpatterns = [
    path('create/', CreateConversationAPIView.as_view(), name='Create Conversation'),
    path('conversation-list/', ChatListAPIView.as_view(), name='Message List'),
    path('conversation-detail/<uuid:conv_id>/', ConversationDetailView.as_view(), name='Conversation Detail'),

    # ai chat
    path('ai/', include('messaging.ai_chat.urls')),
]
