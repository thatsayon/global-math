from django.urls import path

from administration.views import (
    MathLevelsListView,
)

from .views import (
    RegisterView,
    LoginView,
    ForgetPassView,
    ForgetPassOTPVerifyView,
    ForgettedPasswordSetView,
    ResendForgetPassOTPView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='Register View'),
    path('login/', LoginView.as_view(), name='Login View'),
    path('forget-password/', ForgetPassView.as_view(), name='Forget Password'),
    path('otp-verify/', ForgetPassOTPVerifyView.as_view(), name='OTP Verify'),
    path('set-password/', ForgettedPasswordSetView.as_view(), name='Set Password'),
    path('resend-otp/', ResendForgetPassOTPView.as_view(), name='Resend OTP'),
    path('levels/', MathLevelsListView.as_view(), name='Math Levels'),
]
