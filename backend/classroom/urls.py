from django.urls import path
from .views import (
    CreateClassroomView,
    JoinClassroomView,
)

urlpatterns = [
    path("create-classroom/", CreateClassroomView.as_view(), name="create-classroom"),
    path("join-classroom/", JoinClassroomView.as_view(), name="join-classroom"),
]
