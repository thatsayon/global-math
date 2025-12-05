from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions

from django.db.models import Count
from django.shortcuts import get_object_or_404

from classroom.models import (
    Classroom,
    ClassRoomChallenge,
)
from post.serializers import PostFeedSerializer
from post.models import PostModel

from .serializers import (
    ClassRoomListSerializer,
    ClassRoomChallengeSerializer,
)
from .pagination import ClassroomFeedPagination

class ClassRoomListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassRoomListSerializer
    queryset = Classroom.objects.annotate(
        post_count = Count('posts')
    )

class ClassRoomFeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ClassroomFeedPagination
    
    def get(self, request, class_id):
        classroom = get_object_or_404(Classroom, id=class_id)

        posts = PostModel.objects.filter(classroom=class_id)

        if not posts.exists():
            return Response([], status=status.HTTP_200_OK)
        
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)

        serializer = PostFeedSerializer(paginated_posts, many=True, context={'request': request})

        paginated_response = paginator.get_paginated_response(serializer.data).data

        # Inject classroom info at the top
        final_response = {
            "classroom": {
                "id": str(classroom.id),
                "name": classroom.name,
                "members_count": classroom.members_count
            },
            **paginated_response
        }

        return Response(final_response, status=status.HTTP_200_OK)


class ClassRoomChallengeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassRoomChallengeSerializer
    queryset = ClassRoomChallenge.objects.all()
