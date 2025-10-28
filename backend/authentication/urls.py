from django.urls import path
from .views import (
    RegisterView,
    LoginView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='Register View'),
    path('login/', LoginView.as_view(), name='Login View'),
]
