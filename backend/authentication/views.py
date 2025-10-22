from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = CustomTokenObtainPairSerializer.get_token(user)

        response_data = {
            "msg": "User registered successfully",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh) 
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
