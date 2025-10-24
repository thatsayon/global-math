from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions

from .serializers import (
    PostSerializer
)
from .models import (
    PostModel
)

class PostCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"msg": "post saved successfully"},
            status=status.HTTP_200_OK
        )
