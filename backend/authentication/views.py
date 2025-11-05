from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now

from .models import (
    OTP
)
from .utils import (
    generate_otp,
    create_otp_token,
    decode_otp_token,
)
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer
)
from .tasks import (
    send_password_reset_email_task,
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            "msg": "User registered successfully"
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

  
class ForgetPassView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {"message": "email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, email=email)

        otp = generate_otp()

        OTP.objects.create(
            user=user,
            otp=otp,
            created_at=now()
        )

        send_password_reset_email_task.delay(
            user.email,
            user.first_name,
            otp
        )

        passResetToken = create_otp_token(user.id)

        response = Response(
            {
                "msg": "OTP send successfully",
                "user": {
                    "id": str(user.id),
                    "email": user.email
                },
                "passResetToken": passResetToken
            }
        )
        
        response.set_cookie(
            key="passResetToken",
            value=passResetToken,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=60*5,
            path='/',
        )

        return response
