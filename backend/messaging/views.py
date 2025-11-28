from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models import Max, Count, Q, Prefetch
from django.contrib.auth import get_user_model
from .models import Conversation, ConversationParticipant, Message
from .serializers import ConversationSerializer
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


class CreateConversationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        other_user_id = request.data.get("user_id")

        if not other_user_id:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if str(user.id) == str(other_user_id):
            return Response({"detail": "Cannot create conversation with yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if conversation already exists
        existing_convo = (
            Conversation.objects.filter(is_group=False)
            .filter(participants__user=user)
            .filter(participants__user=other_user)
            .first()
        )

        if existing_convo:
            # Inject unread_count for serializer
            existing_convo.unread_count = (
                existing_convo.messages
                .filter(is_read=False)
                .exclude(sender=user)
                .count()
            )

            serializer = ConversationSerializer(existing_convo, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Create new conversation
        conversation = Conversation.objects.create(is_group=False)

        ConversationParticipant.objects.create(user=user, conversation=conversation)
        ConversationParticipant.objects.create(user=other_user, conversation=conversation)

        # Manually inject unread_count since no messages yet
        conversation.unread_count = 0

        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Subquery to fetch the last message per conversation
        last_message_subquery = Message.objects.filter(
            conversation=OuterRef('pk')
        ).order_by('-created_at')

        # Fetch only 1-on-1 conversations for this user
        conversations = (
            Conversation.objects.filter(participants__user=user, is_group=False)
            .annotate(
                last_message_time=Max('messages__created_at'),
                last_message_content=Subquery(last_message_subquery.values('content')[:1]),
                last_message_sender=Subquery(last_message_subquery.values('sender__email')[:1]),
                unread_count=Count(
                    'messages',
                    filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
                )
            )
            .prefetch_related(
                'participants__user'
            )
            .order_by('-last_message_time')
        )

        # Paginate
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(conversations, request)
        serializer = ConversationSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
