from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Classroom, ClassroomMemberList
from .serializers import JoinClassroomSerializer

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

