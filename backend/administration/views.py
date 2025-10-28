from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, static, permissions, status

from .serializers import (
    OverViewSerializer
)

class OverView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser
    ]

    def get(self, request):
        serializer = OverViewSerializer(context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
