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
    UpdateClassroomChallengeView,
    DeleteClassroomChallengeView,
    CreateQuestionWithOptionsView,
    ChallengeQuestionListView,
    UpdateQuestionWithOptionsView,
    DeleteQuestionView,
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
    path('challenge-update/<uuid:pk>/', UpdateClassroomChallengeView.as_view(), name='Update Classroom'),
    path('challenge-delete/<uuid:pk>/', DeleteClassroomChallengeView.as_view(), name='Delete Classroom'),
    path('question-create/', CreateQuestionWithOptionsView.as_view(), name='Question Create'),
    path('question-list/', ChallengeQuestionListView.as_view(), name='Question List'),
    path('question-update/<uuid:question_id>/', UpdateQuestionWithOptionsView.as_view(), name='Question Update'),
    path('question-delete/<uuid:question_id>/', DeleteQuestionView.as_view(), name='Question Delete'),
]
