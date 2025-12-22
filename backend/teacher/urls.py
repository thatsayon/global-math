from django.urls import path
from classroom.views import (
    CreateClassroomView,
)

from .views import (
    ProfileView,
    MyClassroomView,
    ClassroomDetailView,
    InviteStudentView,

    # challenge list views
    ChallengeListView,
    CreateClassroomChallengeView,
    CreateQuestionWithOptionsView,
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='Profile View'),
    path('my-classroom/', MyClassroomView.as_view(), name='My Classroom'),
    path('create-classroom/', CreateClassroomView.as_view(), name='Create Classroom'),
    path('classroom-detail/', ClassroomDetailView.as_view(), name='Classroom Detail'),
    path('invite-student/', InviteStudentView.as_view(), name='Invite Student'),

    # challenge list urls
    path('challenge-list/', ChallengeListView.as_view(), name='Challenge List'),
    path('challenge-create/', CreateClassroomChallengeView.as_view(), name='Challenge Create'),
    path('question-create/', CreateQuestionWithOptionsView.as_view(), name='Question Create'),
]
