from rest_framework.response import Response
from rest_framework import views, status, permissions, generics

from .serializers import (
    ProfileInformationSerializer,
)

class ProfileInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileInformationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
