from django.urls import path
from .views import (
    OverView,
    UserManagementView,
    ModerationView,
    BanUserView,
    UnbanUserView,
)

urlpatterns = [
    path('overview/', OverView.as_view(), name='Over View'),
    path('user-management/', UserManagementView.as_view(), name='User Management'),
    path('moderation/', ModerationView.as_view(), name='User Management'),
    path('ban/', BanUserView.as_view(), name='User Ban'),
    path('unban/', UnbanUserView.as_view(), name='User Unban'),
]
