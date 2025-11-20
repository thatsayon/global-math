from django.urls import path
from classroom.views import (
    JoinClassroomView
)

from .views import (
    ProfileInformationView,
)

urlpatterns = [
    path('join-class/', JoinClassroomView.as_view(), name='Join Classroom'),

    # profile views
    path('profile-information/', ProfileInformationView.as_view(), name='Profile Information')
]
