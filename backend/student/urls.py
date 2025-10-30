from django.urls import path
from classroom.views import (
    JoinClassroomView
)

urlpatterns = [
    path('join-class/', JoinClassroomView.as_view(), name='Join Classroom'),
]
