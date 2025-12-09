from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions

from student.profile.pagination import ProfileFeedPagination

from post.models import (
    PostModel,
)
from post.serializers import (
    PostFeedSerializer,
)
from .serializers import (
    ProfileTopSerializer,
)

class ProfileTopPartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileTopSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileFeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        posts = PostModel.objects.filter(user=request.user).order_by('-created_at')

        paginator = ProfileFeedPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)

        serializer = PostFeedSerializer(
            posts, 
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)
