from django.urls import path
from .views import (
    ProfileTopPartView,
    ProfileFeedView,
)

urlpatterns = [
    path('top/', ProfileTopPartView.as_view(), name='Profile Top'),
    path('feed/', ProfileFeedView.as_view(), name='Profile Feed'),
]
