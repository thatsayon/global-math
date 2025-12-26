from django.urls import path

from .views import (
    DashboardView,
    ChallengeListView,
    LeaderboardView,

    JoinChallengeView,
    NextChallengeQuestionView,
    SubmitSolutionView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='Challenge Dashboard'),
    path('list/', ChallengeListView.as_view(), name='Challenge List'),
    path('leaderboard/', LeaderboardView.as_view(), name='Leaderboard'),

    path('join-challenge/<uuid:challenge_id>/', JoinChallengeView.as_view(), name='Join Challenge'),
    path('challenge-question/<uuid:challenge_id>/', NextChallengeQuestionView.as_view(), name='Next Challenge'),
    path('submit-solution/', SubmitSolutionView.as_view(), name='Submit Solution'),
]
