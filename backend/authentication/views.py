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
        
        return response


class ForgetPassOTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request): 
        otp = request.data.get("otp")
        reset_token = request.data.get("passResetToken")
        
        if not otp or not reset_token:
            return Response({"error": "OTP and reset token are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        decoded = decode_otp_token(reset_token)
        if not decoded:
            return Response({"error": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = decoded.get("user_id")

        user = get_object_or_404(User, id=user_id)

        otp_instance = user.otps.filter(otp=otp).first()
        if not otp_instance or not otp_instance.is_valid():
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        # If OTP is valid, generate a verified token indicating that the OTP step is complete.
        verified_payload = {"user_id": str(user.id), "verified": True}
        verified_token = create_otp_token(verified_payload)
        
        # Optionally, delete the used OTP instance to prevent reuse.
        otp_instance.delete()
        
        response = Response(
            {
                "msg": "OTP verified. You can now reset your password.",
                "passwordResetVerified": verified_token
            }, 
            status=status.HTTP_200_OK
        )

        return response


class ForgettedPasswordSetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        new_password = request.data.get("new_password")
        verified_token = request.data.get("passwordResetVerified")
        
        if not new_password or not verified_token:
            return Response({"error": "New password and verified token are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        decoded = decode_otp_token(verified_token)
        if not decoded or not decoded.get("verified"):
            return Response({"error": "Invalid or expired verified token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = decoded.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Set the new password
        user.set_password(new_password)
        user.save()
        
        response = Response({"msg": "Password reset successfully."}, status=status.HTTP_200_OK)
        # Remove the verified token (and optionally the original reset token)
        return response


class ResendForgetPassOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        reset_token = request.data.get("passResetToken")
        if not reset_token:
            return Response({"error": "No reset token found."}, status=status.HTTP_400_BAD_REQUEST)

        decoded = decode_otp_token(reset_token)
        if not decoded:
            return Response({"error": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)

        user_id = decoded.get("user_id")
        user = get_object_or_404(User, id=user_id)

        otp = generate_otp()
        OTP.objects.create(user=user, otp=otp, created_at=now())

        send_password_reset_email_task.delay(user.email, user.first_name, otp)

        return Response(
            {"message": "Password reset OTP resent successfully to your email."},
            status=status.HTTP_200_OK
        )
