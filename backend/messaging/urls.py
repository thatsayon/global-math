from django.urls import path, include
from .views import (
    CreateConversationAPIView,
    ChatListAPIView,
    ConversationDetailView,
    BlockUserAPIView,
    ReportUserAPIView,
    PinConversationAPIView,
    DeleteConversationAPIView,
)

urlpatterns = [
    path('create/', CreateConversationAPIView.as_view(), name='Create Conversation'),
    path('conversation-list/', ChatListAPIView.as_view(), name='Message List'),
    path('conversation-detail/<uuid:conv_id>/', ConversationDetailView.as_view(), name='Conversation Detail'),
    path('block/', BlockUserAPIView.as_view(), name='Block User'),
    path('report/', ReportUserAPIView.as_view(), name='Report User'),
    path('pin/', PinConversationAPIView.as_view(), name='Pin Conversation'),
    path('delete/', DeleteConversationAPIView.as_view(), name='Delete Conversation'),

    # ai chat
    path('ai/', include('messaging.ai_chat.urls')),
]
