from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import generics, status, permissions

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Max

from classroom.models import (
    Classroom,
    ClassroomMemberList,
    ClassRoomChallenge,
)
from post.models import (
    PostModel,
)

from .serializers import (
    ProfileSerializer,
    MyClassroomSerializer,
    ClassroomDetailSerializer,
    ClassroomMemberSerializer,

    # classroom related serializers
    ClassroomChallengeListSerializer,
    ClassroomChallengeCreateSerializer,
    QuestionWithOptionsCreateSerializer,
)
from .pagination import (
    ClassroomMemberPagination,
)

import os

User = get_user_model()

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class MyClassroomView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MyClassroomSerializer

    def get_queryset(self):
        queryset = (
            Classroom.objects
            .filter(creator=self.request.user)
            .annotate(
                last_activity=Max("posts__created_at") 
            )
        )

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search) |
                Q(room_code__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)

        total_classes = queryset.count()
        total_students = queryset.aggregate(total=Sum("members_count"))["total"] or 0
        total_posts = PostModel.objects.filter(classroom__in=queryset).count()

        return Response({
            "total_classes": total_classes,
            "total_posts": total_posts,
            "students": total_students,
            "results": serializer.data,
        })



class ClassroomDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassroomDetailSerializer
    pagination_class = ClassroomMemberPagination

    def get_object(self):
        classroom_id = self.request.query_params.get("id")

        if not classroom_id:
            raise ValidationError(
                {"id": "classroom id query parameter is required"}
            )

        return get_object_or_404(Classroom, id=classroom_id)

    def retrieve(self, request, *args, **kwargs):
        classroom = self.get_object()

        # Static classroom data
        classroom_data = self.get_serializer(classroom).data

        # Paginated members
        members_qs = (
            ClassroomMemberList.objects
            .filter(classroom=classroom)
            .select_related("user")
            .order_by("-joined_at")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(members_qs, request)

        members_data = ClassroomMemberSerializer(page, many=True).data
        members_pagination = paginator.get_paginated_response(members_data).data

        return Response({
            "classroom": classroom_data,
            "members": members_pagination
        })

class InviteStudentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        classroom_id = request.query_params.get("id")

        if not classroom_id:
            raise ValidationError(
                {"id": "classroom_id is required"}
            )

        classroom = get_object_or_404(Classroom, id=classroom_id)

        share_url = os.getenv('FRONTEND_BASE') + "/" + classroom.room_code
        print(classroom.room_code)
        return Response({
            "classroom link": share_url
        }, status=status.HTTP_200_OK)

# classroom related views

class ChallengeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassroomChallengeListSerializer

    def get_queryset(self):
        user = self.request.user
        classroom_id = self.request.query_params.get("classroom_id")

        if not classroom_id:
            raise ValidationError(
                {"classroom_id": "classroom_id query parameter is required"}
            )

        classroom = get_object_or_404(Classroom, id=classroom_id)

        # Access control: teacher or member only
        if (
            classroom.creator != user
            and not classroom.members.filter(user=user).exists()
        ):
            return ClassRoomChallenge.objects.none()

        return ClassRoomChallenge.objects.filter(
            classroom=classroom
        ).select_related("classroom")


class CreateClassroomChallengeView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassroomChallengeCreateSerializer

    def get_serializer_context(self):
        return {"request": self.request}

class UpdateClassroomChallengeView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassroomChallengeCreateSerializer
    queryset = ClassRoomChallenge.objects.all()
    http_method_names = ["patch", "put"]

    def perform_update(self, serializer):
        challenge = self.get_object()
        user = self.request.user

        if challenge.classroom.creator != user:
            raise PermissionDenied(
                "You are not allowed to update this challenge."
            )

        serializer.save()


class DeleteClassroomChallengeView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ClassRoomChallenge.objects.all()

    def perform_destroy(self, instance):
        user = self.request.user

        if instance.classroom.creator != user:
            raise PermissionDenied(
                "You are not allowed to delete this challenge."
            )

        instance.delete()

class CreateQuestionWithOptionsView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionWithOptionsCreateSerializer

    def get_serializer_context(self):
        return {"request": self.request}
