from django.urls import path
from .views import (
    CreateChatSessionView,
    SendChatMessageView,
)

urlpatterns = [
    path('chat-session/', CreateChatSessionView.as_view(), name='Create Chat Session'),
    path('chat/', SendChatMessageView.as_view(), name='Send Chat'),
]
