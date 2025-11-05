from django.urls import path

from administration.views import (
    MathLevelsListView,
)

from .views import (
    RegisterView,
    LoginView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='Register View'),
    path('login/', LoginView.as_view(), name='Login View'),
    path('levels/', MathLevelsListView.as_view(), name='Math Levels'),
]
