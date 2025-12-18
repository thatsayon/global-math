from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

from .models import ChatSession, ChatMessage, MessageRole
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .pagination import ChatMessagePagination

import requests
import os

AI_CHAT_BASE = os.getenv('AI_CHAT_BASE_URL')

class CreateChatSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # 1. Check if session already exists
        existing_session = ChatSession.objects.filter(user=user).first()
        if existing_session:
            serializer = ChatSessionSerializer(existing_session)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        # 2. Create new AI session
        try:
            res = requests.post(
                f"{AI_CHAT_BASE}/api/set_email/",
                json={"email": user.email},
                timeout=10
            )
            res.raise_for_status()
        except requests.RequestException:
            return Response(
                {"error": "AI service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        ai_session_id = res.json().get("session_id")
        if not ai_session_id:
            return Response(
                {"error": "Invalid AI response"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # 3. Save session
        session = ChatSession.objects.create(
            user=user,
            ai_session_id=ai_session_id
        )

        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SendChatMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Sends user message to AI and stores both user + AI messages
        """
        session_id = request.data.get("session_id")
        message = request.data.get("message")

        if not session_id or not message:
            return Response(
                {"error": "session_id and message are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        session = ChatSession.objects.filter(
            ai_session_id=session_id,
            user=request.user
        ).first()


        if not session:
            return Response(
                {"error": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role=MessageRole.USER,
            content=message
        )

        # Send to AI
        try:
            res = requests.post(
                f"{AI_CHAT_BASE}/api/chat/",
                json={
                    "message": message,
                    "session_id": session.ai_session_id
                },
                timeout=30
            )
            res.raise_for_status()
        except requests.RequestException:
            return Response(
                {"error": "AI service failed"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        data = res.json()
        ai_reply = data.get("response")

        if not ai_reply:
            return Response(
                {"error": "Invalid AI response"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # Save AI message
        ai_msg = ChatMessage.objects.create(
            session=session,
            role=MessageRole.ASSISTANT,
            content=ai_reply
        )

        return Response(
            {
                "user_message": ChatMessageSerializer(user_msg).data,
                "ai_message": ChatMessageSerializer(ai_msg).data,
            },
            status=status.HTTP_200_OK
        )



class GetChatMessagesView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer
    pagination_class = ChatMessagePagination

    def get(self, request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "session_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # IMPORTANT: session_id here is ai_session_id (your current contract)
        session = ChatSession.objects.filter(
            ai_session_id=session_id,
            user=request.user
        ).first()

        if not session:
            return Response(
                {"error": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = ChatMessage.objects.filter(
            session=session
        ).order_by("created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
