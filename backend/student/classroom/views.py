from rest_framework.views import APIView
from rest_framework import generics, status, permissions

from classroom.models import Classroom

from .serializers import (
    ClassRoomListSerializer,
)

class ClassroomListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassRoomListSerializer
    queryset = Classroom.objects.all()
