from django.urls import path
from student.views import (
    StudentDashboardView,
)
from .views import (
    ProfileTopPartView,
    ProfileFeedView,
)

urlpatterns = [
    path('top/', ProfileTopPartView.as_view(), name='Profile Top'),
    path('feed/', ProfileFeedView.as_view(), name='Profile Feed'),
    path('activity/', StudentDashboardView.as_view(), name='Dashboard'),
]
