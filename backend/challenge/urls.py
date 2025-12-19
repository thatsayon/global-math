from django.urls import path

from .views import (
    DashboardView,
    ChallengeListView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='Challenge Dashboard'),
    path('list/', ChallengeListView.as_view(), name='Challenge List'),
]
