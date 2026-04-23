from django.urls import path
from .views import (
    CreateClassroomView,
    JoinClassroomView,
    ListJoinRequestsView,
    RespondJoinRequestView,
)

urlpatterns = [
    path("create-classroom/", CreateClassroomView.as_view(), name="create-classroom"),
    path("join-classroom/", JoinClassroomView.as_view(), name="join-classroom"),
    path("join-requests/", ListJoinRequestsView.as_view(), name="join-requests-list"),
    path("join-requests/respond/", RespondJoinRequestView.as_view(), name="join-requests-respond"),
]

