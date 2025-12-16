from django.urls import path
from .views import (
    ClassRoomListView,
    ClassRoomFeedView,
    ClassRoomChallengeListView,
    AttendChallengeView,
    SubmitAnswerView,
    BrowserClassroomView,
    JoinClassroomView,
    JoinClassroomWithCode,
    ClassroomLeaderboardView,
)

urlpatterns = [
    path('list/', ClassRoomListView.as_view(), name='Classroom List'),
    path('feed/<uuid:class_id>/', ClassRoomFeedView.as_view(), name='Classroom Feed'),
    path('challenge/<uuid:classroom_id>/', ClassRoomChallengeListView.as_view(), name='Classroom Challenege'),
    path('challenge-attend/<uuid:challenge_id>/', AttendChallengeView.as_view(), name='Attend Challenege'),
    path('submit-answer/<uuid:challenge_id>/<uuid:question_id>/', SubmitAnswerView.as_view(), name='Attend Challenege'),
    path('browse/', BrowserClassroomView.as_view(), name='Browse Classroom'),
    path('join/<uuid:classroom_id>/', JoinClassroomView.as_view(), name='Join Classroom'),
    path('join-with-code/<str:room_code>/', JoinClassroomWithCode.as_view(), name='Join Classroom'),
    path('leaderboard/<uuid:classroom_id>/', ClassroomLeaderboardView.as_view(), name='Leaderboard'),
]
