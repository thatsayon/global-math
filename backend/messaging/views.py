from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models import Max, Count, Q, Prefetch, F, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models import CharField
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


class ConversationMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id, *args, **kwargs):
        user = request.user
        try:
            conversation = Conversation.objects.get(id=conversation_id, participants__user=user)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND)

        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        data = [
            {
                "id": str(m.id),
                "sender": m.sender.email,
                "content": m.content,
                "timestamp": m.created_at.isoformat(),
                "is_me": m.sender == user
            } for m in messages
        ]
        return Response(data, status=status.HTTP_200_OK)

