from django.urls import path
from .views import (
    OverView
)

urlpatterns = [
    path('overview/', OverView.as_view(), name='Over View'),
]
