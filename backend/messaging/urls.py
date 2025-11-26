from django.urls import path
from .views import (
    ChatListAPIView
)

urlpatterns = [
    path('conversation-list/', ChatListAPIView.as_view(), name='Message List'),
]
