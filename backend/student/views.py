from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import views, status, permissions, generics

from django.shortcuts import get_object_or_404

from administration.models import (
    SupportTicket,
    SupportMessage,
)

from .serializers import (
    ProfileInformationSerializer,
    ChangePasswordSerializer,
    SupportMessageSerializer,
)

class ProfileInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileInformationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)

class HelpSupportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ticket = SupportTicket.objects.filter(
            user=request.user,
            is_closed=False
        ).first()

        if not ticket:
            return Response({
                "messages": [],
                "detail": "No active support ticket."
            }, status=status.HTTP_200_OK)

        paginator = PageNumberPagination()
        queryset = ticket.messages.all()  # ordered oldest → newest in model Meta
        paginated_messages = paginator.paginate_queryset(queryset, request)

        serializer = SupportMessageSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response({
            "ticket_id": ticket.id,
            "messages": serializer.data
        })

    def post(self, request):
        msg = request.data.get('msg')
        if not msg:
            return Response({
                "error": "message is required"
            }, status=status.HTTP_400_BAD_REQUEST)


        ticket = SupportTicket.objects.filter(
            user=request.user,
            is_closed=False
        ).first()

        if not ticket:
            ticket = SupportTicket.objects.create(user=request.user)

        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=msg
        )

        return Response(
            {"message": "Message sent successfully", "ticket_id": ticket.id},
            status=status.HTTP_201_CREATED
        )

