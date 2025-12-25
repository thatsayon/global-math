from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import views, status, permissions, generics

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone

from datetime import timedelta

from administration.models import (
    SupportTicket,
    SupportMessage,
)

from .serializers import (
    ProfileInformationSerializer,
    ChangePasswordSerializer,
    SupportMessageSerializer,
    OtherProfileSerializer,
    LatestPostSerializer,
    StudentDashboardSerializer,
)
from .pagination import (
    LatestPostPagination,
)
from .utils import (
    add_points,
    calculate_streaks,
)

User = get_user_model()

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



class OtherProfileView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # paginate posts
        posts_qs = user.posts.order_by("-created_at")
        paginator = LatestPostPagination()
        page = paginator.paginate_queryset(posts_qs, request)

        posts_data = LatestPostSerializer(page, many=True).data

        # build paginated structure manually
        latest_post = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": posts_data,
        }

        user_data = OtherProfileSerializer(user).data
        user_data["latest_post"] = latest_post

        return Response(user_data)


class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        student = request.user.account.student
        progress = student.progress
        today = timezone.now().date()

        # activity map
        activities = (
            student.daily_activities
            .values("date")
            .annotate(points=Sum("points_earned"))
        )

        activity_map = {
            a["date"]: a["points"]
            for a in activities
        }

        active_dates = [
            d for d, p in activity_map.items() if p > 0
        ]

        current_streak, longest_streak = calculate_streaks(active_dates)

        # calendar (last 30 days)
        calendar = []
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            points = activity_map.get(day, 0)

            calendar.append({
                "date": day,
                "points": points,
                "active": points > 0
            })

        next_level_points = (
            progress.BASE_POINTS * (progress.level + 1) ** 2
        )

        data = {
            "progress": {
                "total_points": progress.total_points,
                "level": progress.level,
                "next_level_points": next_level_points,
                "points_to_next_level": max(
                    next_level_points - progress.total_points, 0
                )
            },
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "calendar": calendar,
            "badges": student.earned_badges.select_related("badge")
        }

        serializer = StudentDashboardSerializer(data)
        return Response(serializer.data)
