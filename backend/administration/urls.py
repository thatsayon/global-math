from django.urls import path
from .views import (
    OverView,
    UserManagementView,
    ModerationView,
    BanUserView,
    UnbanUserView,

    # profile views
    AdminProfileAPIView,
    ChangePasswordAPIView,
    LevelAdjustmentView,
    LevelAdjustmentUpdateView,
    LevelDeleteView,
)

urlpatterns = [
    path('overview/', OverView.as_view(), name='Over View'),
    path('user-management/', UserManagementView.as_view(), name='User Management'),
    path('moderation/', ModerationView.as_view(), name='User Management'),
    path('ban/', BanUserView.as_view(), name='User Ban'),
    path('unban/', UnbanUserView.as_view(), name='User Unban'),

    # profile urls
    path('profile/', AdminProfileAPIView.as_view(), name='Profile'),
    path('update-password/', ChangePasswordAPIView.as_view(), name='Change Password'),
    path('level-adjustment/', LevelAdjustmentView.as_view(), name='Level Adjustment'),
    path('level-adjustment/<uuid:id>/', LevelAdjustmentUpdateView.as_view(), name='Level Adjustment Update'),
    path('level-delete/<uuid:id>/', LevelDeleteView.as_view(), name='Level Adjustment Update'),
]
