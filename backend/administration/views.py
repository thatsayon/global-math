from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, static, permissions, status, filters

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    OverViewSerializer,
    UserManagementSerializer,
    ModerationSerializer,
)

User = get_user_model()

class AdminBaseView:
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    ]

class OverView(AdminBaseView, APIView):
    def get(self, request):
        serializer = OverViewSerializer({}, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserManagementView(AdminBaseView, generics.ListAPIView):
    serializer_class = UserManagementSerializer
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name", "email"]
    filterset_fields = ["role", "is_banned"]

class ModerationView(AdminBaseView, APIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name", "email"]
    filterset_fields = ["is_banned"]

    def get(self, request):
        users = User.objects.filter(role="student")

        for backend in list(self.filter_backends):
            users = backend().filter_queryset(self.request, users, self)

        data = {
            "top": {},
            "users": users,
        }

        serializer = ModerationSerializer(instance=data, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class BanUserView(AdminBaseView, APIView):
    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_banned:
            return Response(
                {"msg": f"User '{user.username}' is already banned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_banned = True
        user.save()

        return Response(
            {"msg": f"User '{user.username}' has been banned"},
            status=status.HTTP_200_OK
        )

class UnbanUserView(AdminBaseView, APIView):
    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.is_banned:
            return Response(
                {"msg": f"User '{user.username}' is not banned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_banned = False
        user.save()

        return Response(
            {"msg": f"User '{user.username}' has been unbanned"},
            status=status.HTTP_200_OK
        )

