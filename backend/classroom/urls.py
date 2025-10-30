from django.urls import path
from .views import (
    JoinClassroomView,
)

urlpatterns = [
    path("join-classroom/", JoinClassroomView.as_view(), name="join-classroom"),
]
