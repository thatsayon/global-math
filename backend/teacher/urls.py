from django.urls import path
from classroom.views import (
    CreateClassroomView,
)

urlpatterns = [
    path('create-classroom/', CreateClassroomView.as_view(), name='Create Classroom'),
]
