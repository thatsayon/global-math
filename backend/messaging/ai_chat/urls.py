from django.urls import path
from .views import (
    CreateChatSessionView,
    SendChatMessageView,
    GetChatMessagesView,
)

urlpatterns = [
    path('chat-session/', CreateChatSessionView.as_view(), name='Create Chat Session'),
    path('chat/', SendChatMessageView.as_view(), name='Send Chat'),
    path('messages/', GetChatMessagesView.as_view(), name='Chat Message'),
]
