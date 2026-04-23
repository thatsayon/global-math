from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics

from core.activity_logger import log_classroom_created

from .models import Classroom, ClassroomMemberList, JoinRequest
from .serializers import (
    JoinClassroomSerializer,
    CreateClassroomSerializer,
    ClassroomDetailSerializer,
    JoinRequestSerializer
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

class UpdateClassroomView(generics.UpdateAPIView):
    serializer_class = CreateClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only the creator can update the classroom
        return Classroom.objects.filter(creator=self.request.user)


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

        if not classroom.is_public:
            if JoinRequest.objects.filter(user=request.user, classroom=classroom, status="pending").exists():
                return Response({"message": "You already have a pending join request."}, status=status.HTTP_200_OK)
            JoinRequest.objects.create(user=request.user, classroom=classroom, status="pending")
            return Response({"message": "Join request sent to the teacher.", "status": "pending"}, status=status.HTTP_201_CREATED)

        member = ClassroomMemberList.objects.create(user=request.user, classroom=classroom)
        classroom.members_count = ClassroomMemberList.objects.filter(classroom=classroom).count()
        classroom.save(update_fields=["members_count"])

        serializer = JoinClassroomSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ListJoinRequestsView(generics.ListAPIView):
    serializer_class = JoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = JoinRequest.objects.filter(classroom__creator=self.request.user, status="pending")
        
        classroom_id = self.request.query_params.get("classroom_id") or self.request.data.get("classroom_id")
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)
            
        return queryset

class RespondJoinRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request_id = request.data.get("request_id")
        action = request.data.get("action")

        if not request_id or action not in ["approve", "reject"]:
            return Response({"error": "request_id and valid action ('approve' or 'reject') are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            join_request = JoinRequest.objects.get(id=request_id, classroom__creator=request.user)
        except JoinRequest.DoesNotExist:
            return Response({"error": "Join request not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        if join_request.status != "pending":
            return Response({"error": "Request is already processed"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "approve":
            join_request.status = "approved"
            join_request.save(update_fields=["status"])
            
            if not ClassroomMemberList.objects.filter(user=join_request.user, classroom=join_request.classroom).exists():
                ClassroomMemberList.objects.create(user=join_request.user, classroom=join_request.classroom)
                classroom = join_request.classroom
                classroom.members_count = ClassroomMemberList.objects.filter(classroom=classroom).count()
                classroom.save(update_fields=["members_count"])
            
            return Response({"message": "Join request approved."}, status=status.HTTP_200_OK)
        else:
            join_request.status = "rejected"
            join_request.save(update_fields=["status"])
            return Response({"message": "Join request rejected."}, status=status.HTTP_200_OK)

