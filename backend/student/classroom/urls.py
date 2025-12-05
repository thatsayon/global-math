from django.urls import path
from .views import (
    ClassRoomListView,
    ClassRoomFeedView,
    ClassRoomChallengeListView,
)

urlpatterns = [
    path('list/', ClassRoomListView.as_view(), name='Classroom List'),
    path('feed/<uuid:class_id>/', ClassRoomFeedView.as_view(), name='Classroom Feed'),
    path('challenge/', ClassRoomChallengeListView.as_view(), name='Classroom Challenege'),
]
