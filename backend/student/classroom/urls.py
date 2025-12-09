from django.urls import path
from .views import (
    ClassRoomListView,
    ClassRoomFeedView,
    ClassRoomChallengeListView,
    AttendChallengeView,
    SubmitAnswerView,
)

urlpatterns = [
    path('list/', ClassRoomListView.as_view(), name='Classroom List'),
    path('feed/<uuid:class_id>/', ClassRoomFeedView.as_view(), name='Classroom Feed'),
    path('challenge/', ClassRoomChallengeListView.as_view(), name='Classroom Challenege'),
    path('challenge-attend/<uuid:challenge_id>/', AttendChallengeView.as_view(), name='Attend Challenege'),
    path('submit-answer/<uuid:challenge_id>/<uuid:question_id>/', SubmitAnswerView.as_view(), name='Attend Challenege'),
]
