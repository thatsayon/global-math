from django.urls import path

from administration.views import (
    MathLevelsListView,
)

from .views import (
    RegisterView,
    LoginView,
    ForgetPassView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='Register View'),
    path('login/', LoginView.as_view(), name='Login View'),
    path('forget-password/', ForgetPassView.as_view(), name='Forget Password'),
    path('levels/', MathLevelsListView.as_view(), name='Math Levels'),
]
