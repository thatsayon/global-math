from django.urls import path, include
from classroom.views import (
    JoinClassroomView
)

from .views import (
    ProfileInformationView,
    ChangePasswordView,
    HelpSupportView,
    OtherProfileView,
    StudentDashboardView,
)

urlpatterns = [
    path('join-class/', JoinClassroomView.as_view(), name='Join Classroom'),

    # profile views
    path('profile-information/', ProfileInformationView.as_view(), name='Profile Information'),
    path('change-password/', ChangePasswordView.as_view(), name='Change Password'),
    path('help-support/', HelpSupportView.as_view(), name='Help Suppport'),

    # class room views
    path('classroom/', include('student.classroom.urls')),

    path('profile/', include('student.profile.urls')),
    path('other-profile/<uuid:user_id>/', OtherProfileView.as_view(), name='Other User'),
]
