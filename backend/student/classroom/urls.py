from django.urls import path
from .views import (
    ClassroomListView,
)

urlpatterns = [
    path('list/', ClassroomListView.as_view(), name='Classroom List'),
]
