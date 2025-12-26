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

    # setting views
    PointAdjustmentView,
    AnalyticsReportAPIView,

    # ai question generation
    ChallengeGenerationView,
    CreateDailyChallengeView,
    DailyChallengeListView,
    DailyChallengeUpdateView,
    DailyChallengeDeleteView,
    ChallengeQuestionListView,
    ChallengeQuestionUpdateView,
    ChallengeQuestionDeleteView,

    # support views
    SupportInboxView,
    SupportMessageListView,
    SupportReplyView,
)

urlpatterns = [
    path('overview/', OverView.as_view(), name='Over View'),
    path('user-management/', UserManagementView.as_view(), name='User Management'),
    path('moderation/', ModerationView.as_view(), name='User Management'),
    path('ban/', BanUserView.as_view(), name='User Ban'),
    path('unban/', UnbanUserView.as_view(), name='User Unban'),
    path('analytics/', AnalyticsReportAPIView.as_view(), name='Analytics'),

    # profile urls
    path('profile/', AdminProfileAPIView.as_view(), name='Profile'),
    path('update-password/', ChangePasswordAPIView.as_view(), name='Change Password'),
    path('level-adjustment/', LevelAdjustmentView.as_view(), name='Level Adjustment'),
    path('level-adjustment/<uuid:id>/', LevelAdjustmentUpdateView.as_view(), name='Level Adjustment Update'),
    path('level-delete/<uuid:id>/', LevelDeleteView.as_view(), name='Level Adjustment Update'),

    # setting urls
    path('point-adjustment/', PointAdjustmentView.as_view(), name='Point Adjustment'),


    # ai question generation urls
    path('question-generation/', ChallengeGenerationView.as_view(), name='Challenge Generation'),
    path('create-challenge/', CreateDailyChallengeView.as_view(), name='Create Challenge'),
    path('challenge-list/', DailyChallengeListView.as_view(), name='Daily Challenge'),
    path('challenge-update/<uuid:challenge_id>/', DailyChallengeUpdateView.as_view(), name='Daily Challenge Update'),
    path('challenge-delete/<uuid:challenge_id>/', DailyChallengeDeleteView.as_view(), name='Daily Challenge Delete'),
    path('question-list/<uuid:challenge_id>/', ChallengeQuestionListView.as_view(), name='Question List'),
    path('question-update/<uuid:question_id>/', ChallengeQuestionUpdateView.as_view(), name='Question Update'),
    path('question-delete/<uuid:question_id>/', ChallengeQuestionDeleteView.as_view(), name='Question Delete'),

    # support urls
    path('support-message/', SupportInboxView.as_view(), name='Support View'),
    path('support-message/<uuid:ticket_id>/', SupportMessageListView.as_view(), name='Support Message List'),
    path('support-message-reply/<uuid:ticket_id>/', SupportReplyView.as_view(), name='Support Message Reply'),
]
