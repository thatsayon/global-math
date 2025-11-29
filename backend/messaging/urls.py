from django.urls import path
from .views import (
    CreateConversationAPIView,
    ChatListAPIView,
    ChatDetailView,
)

urlpatterns = [
    path('create/', CreateConversationAPIView.as_view(), name='Create Conversation'),
    path('conversation-list/', ChatListAPIView.as_view(), name='Message List'),
    path('conversation-detail/<uuid:conv_id>/', ChatDetailView.as_view(), name='Conversation Detail'), ]
