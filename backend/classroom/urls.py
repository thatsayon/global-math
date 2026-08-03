from django.urls import path
from .views import (
    CreateClassroomView,
    JoinClassroomView,
    DeleteClassroomView,
    RemoveStudentView,
)

urlpatterns = [
    path("create-classroom/", CreateClassroomView.as_view(), name="create-classroom"),
    path("join-classroom/", JoinClassroomView.as_view(), name="join-classroom"),
    path("delete-classroom/<int:pk>/", DeleteClassroomView.as_view(), name="delete-classroom"),
    path("remove-student/<uuid:classroom_id>/<uuid:student_id>/", RemoveStudentView.as_view(), name="remove-student"),
]

