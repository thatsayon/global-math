from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics

from core.activity_logger import log_classroom_created

from .models import Classroom, ClassroomMemberList
from .serializers import (
    JoinClassroomSerializer,
    CreateClassroomSerializer,
    ClassroomDetailSerializer,
)

class CreateClassroomView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Classroom.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateClassroomSerializer
        return ClassroomDetailSerializer
        
    def perform_create(self, serializer):
        # 1️⃣ Create classroom
        classroom = serializer.save(creator=self.request.user)

        # 2️⃣ Log activity AFTER successful creation
        try:
            log_classroom_created(
                teacher_name=f"{self.request.user.first_name} {self.request.user.last_name}",
                classroom_name=classroom.name
            )
        except:
            pass

class JoinClassroomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        classroom_id = request.data.get("classroom_id")

        if not classroom_id:
            return Response({"error": "classroom_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            classroom = Classroom.objects.get(id=classroom_id)
        except Classroom.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

        if ClassroomMemberList.objects.filter(user=request.user, classroom=classroom).exists():
            return Response({"message": "You already joined this classroom."}, status=status.HTTP_200_OK)

        member = ClassroomMemberList.objects.create(user=request.user, classroom=classroom)
        classroom.members_count = ClassroomMemberList.objects.filter(classroom=classroom).count()
        classroom.save(update_fields=["members_count"])

        serializer = JoinClassroomSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

