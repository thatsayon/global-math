from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max, Count, Q
from .models import Conversation
from .serializers import ConversationSerializer
from rest_framework.pagination import PageNumberPagination

class ChatListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Fetch only 1-on-1 conversations
        conversations = (
            Conversation.objects.filter(participants__user=user, is_group=False)
            .annotate(
                last_message_time=Max('messages__created_at'),
                unread_count=Count(
                    'messages',
                    filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
                )
            )
            .order_by('-last_message_time')
        )

        # Use DRF default pagination
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(conversations, request)
        serializer = ConversationSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

