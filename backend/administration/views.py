from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, static, permissions, status, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import TruncMonth, ExtractYear
from django.db.models import Count, Sum, Max
from django.db import transaction

from datetime import datetime

from account.models import (
    StudentProfile,
)
from administration.models import DailyChallenge, ActivityLog
from .models import (
    MathLevels,
    PointAdjustment,
    DailyChallenge,
    ChallengeQuestion,
)

from .serializers import (
    OverViewSerializer,
    UserManagementSerializer,
    ModerationSerializer,
    MathLevelsSerializer,

    # profile serializer
    AdminProfileSerializer,
    ChangePasswordSerializer,
    LevelAdjustmentSerializer,

    # setting serializers
    PointAdjustmentSerializer,

    # ai question generation serializer
    ChallengeGenerationSerializer,
    ChallengeCreateSerializer,
    DailyChallengeListSerializer,
    DailyChallengeUpdateSerializer,
    ChallengeQuestionSerializer,
)

import os
import requests

User = get_user_model()

class AdminBaseView:
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    ]

class OverView(AdminBaseView, APIView):
    def get(self, request):
        serializer = OverViewSerializer({}, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserManagementView(AdminBaseView, generics.ListAPIView):
    serializer_class = UserManagementSerializer
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name", "email"]
    filterset_fields = ["role", "is_banned"]

class ModerationView(AdminBaseView, APIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name", "email"]
    filterset_fields = ["is_banned", "role"]

    def get(self, request):
        users = User.objects.all()

        for backend in list(self.filter_backends):
            users = backend().filter_queryset(self.request, users, self)

        data = {
            "top": {},
            "users": users,
        }

        serializer = ModerationSerializer(
            instance=data,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class BanUserView(AdminBaseView, APIView):
    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_banned:
            return Response(
                {"msg": f"User '{user.username}' is already banned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_banned = True
        user.save()

        return Response(
            {"msg": f"User '{user.username}' has been banned"},
            status=status.HTTP_200_OK
        )

class UnbanUserView(AdminBaseView, APIView):
    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.is_banned:
            return Response(
                {"msg": f"User '{user.username}' is not banned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_banned = False
        user.save()

        return Response(
            {"msg": f"User '{user.username}' has been unbanned"},
            status=status.HTTP_200_OK
        )

class MathLevelsListView(generics.ListAPIView):
    queryset = MathLevels.objects.all().order_by("name")  
    serializer_class = MathLevelsSerializer
    permission_classes = [permissions.AllowAny]  
    pagination_class = None

class AdminProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminProfileSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordAPIView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK
        )

class LevelAdjustmentView(generics.ListCreateAPIView):
    serializer_class = LevelAdjustmentSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = MathLevels.objects.all()

class LevelAdjustmentUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = LevelAdjustmentSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = MathLevels.objects.all()
    lookup_field = 'id'

class LevelDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = MathLevels.objects.all()
    lookup_field = 'id'

class PointAdjustmentView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PointAdjustmentSerializer

    def get_object(self):
        obj, _ = PointAdjustment.objects.get_or_create(
            defaults={
                "classroom_point": 0,
                "upvote_point": 0,
                "daily_challenge_point": 0,
            }
        )
        return obj


class ChallengeGenerationView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = ChallengeGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ai_base_url = os.getenv("AI_BASE_URL")
        if not ai_base_url:
            return Response(
                {"error": "AI_BASE_URL is not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        payload = {
            "grade": serializer.validated_data["dificulty_level"],
            "subject": serializer.validated_data["subject"],
            "count": serializer.validated_data["number_of_question"],
        }

        try:
            ai_response = requests.post(
                f"{ai_base_url}/generate-question",
                data=payload,          # 👈 THIS is form-data / x-www-form-urlencoded
                timeout=20
            )
        except requests.RequestException as e:
            return Response(
                {"error": "Failed to reach AI service", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if ai_response.status_code != 200:
            return Response(
                {
                    "error": "AI service error",
                    "status_code": ai_response.status_code,
                    "response": ai_response.text,
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(ai_response.json(), status=status.HTTP_200_OK)

class CreateDailyChallengeView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @transaction.atomic
    def post(self, request):
        serializer = ChallengeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        challenge = DailyChallenge.objects.create(
            name=data["name"],
            description=data["description"],
            subject=data["subject"],
            grade=data["grade"],
            points=data["points"],
            number_of_questions=len(data["questions"]),
            publishing_date=data["publishing_date"],
            image=request.FILES.get("image"),
        )

        questions = [
            ChallengeQuestion(
                challenge=challenge,
                order=q["order"],
                question_text=q["question_text"],
                answer=q["answer"],
            )
            for q in data["questions"]
        ]

        ChallengeQuestion.objects.bulk_create(questions)

        return Response(
            {
                "id": challenge.id,
                "message": "Challenge created successfully"
            },
            status=status.HTTP_201_CREATED
        )

class DailyChallengeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DailyChallengeListSerializer

    def get_queryset(self):
        queryset = DailyChallenge.objects.select_related("subject")

        subject_slug = self.request.query_params.get("subject")

        if subject_slug:
            queryset = queryset.filter(subject__slug=subject_slug)

        return queryset.order_by("-publishing_date")


class DailyChallengeUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = DailyChallengeUpdateSerializer
    queryset = DailyChallenge.objects.all()
    lookup_url_kwarg = "challenge_id"
    http_method_names = ["patch", "put"]



class DailyChallengeDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = DailyChallenge.objects.all()
    lookup_url_kwarg = "challenge_id"


class ChallengeQuestionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ChallengeQuestionSerializer

    def get_queryset(self):
        challenge_id = self.kwargs["challenge_id"]
        return (
            ChallengeQuestion.objects
            .filter(challenge_id=challenge_id)
            .order_by("order")
        )

class ChallengeQuestionUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ChallengeQuestionSerializer
    queryset = ChallengeQuestion.objects.all()
    lookup_url_kwarg = "question_id"
    http_method_names = ["patch", "put"]


class ChallengeQuestionDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = ChallengeQuestion.objects.all()
    lookup_url_kwarg = "question_id"


class AnalyticsPagination(PageNumberPagination):
    page_size = 10

class AnalyticsReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AnalyticsPagination

    def get(self, request):
        year = int(request.query_params.get("year", datetime.now().year))

        # =========================
        # SUMMARY
        # =========================
        summary = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(
                is_active=True,
                is_banned=False
            ).count(),
            "total_challenges": DailyChallenge.objects.count(),
        }

        # =========================
        # AVAILABLE YEARS (for dropdown)
        # =========================
        available_years = (
            User.objects
            .annotate(year=ExtractYear("date_joined"))
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )

        # =========================
        # USAGE ANALYTICS (CHART)
        # =========================
        user_registrations = (
            User.objects
            .filter(date_joined__year=year)
            .annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(users=Count("id"))
        )

        engagement = (
            StudentProfile.objects
            .filter(daily_activities__date__year=year)
            .annotate(month=TruncMonth("daily_activities__date"))
            .values("month")
            .annotate(engagement=Count("id", distinct=True))
        )

        activity = (
            ActivityLog.objects
            .filter(created_at__year=year)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(activity=Count("id"))
        )

        month_map = {}

        def month_key(dt):
            return dt.strftime("%b")

        for row in user_registrations:
            key = month_key(row["month"])
            month_map[key] = {
                "month": key,
                "users": row["users"],
                "engagement": 0,
                "activity": 0,
            }

        for row in engagement:
            key = month_key(row["month"])
            month_map.setdefault(key, {
                "month": key,
                "users": 0,
                "engagement": 0,
                "activity": 0,
            })
            month_map[key]["engagement"] = row["engagement"]

        for row in activity:
            key = month_key(row["month"])
            month_map.setdefault(key, {
                "month": key,
                "users": 0,
                "engagement": 0,
                "activity": 0,
            })
            month_map[key]["activity"] = row["activity"]

        usage_analytics = sorted(
            month_map.values(),
            key=lambda x: datetime.strptime(x["month"], "%b").month
        )

        # =========================
        # STUDENT ENGAGEMENT TABLE
        # =========================
        students_qs = (
            StudentProfile.objects
            .select_related("account__user")
            .annotate(
                total_points=Sum("daily_activities__points_earned"),
                last_active=Max("daily_activities__date"),
            )
            .order_by("-total_points")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(students_qs, request)

        table_data = []
        start_index = paginator.page.start_index()

        for idx, student in enumerate(page, start=start_index):
            user = student.account.user
            points = student.total_points or 0

            engagement_score = min(100, int((points / 500) * 100))

            table_data.append({
                "no": idx,
                "id": str(user.id),
                "name": f"{user.first_name} {user.last_name}",
                "role": user.role,
                "profile_pic": user.profile_pic.url if user.profile_pic else None,
                "challenges": student.daily_activities.count(),
                "engagement_score": engagement_score,
                "last_active": student.last_active,
            })

        student_engagement = paginator.get_paginated_response(table_data).data

        # =========================
        # FINAL RESPONSE
        # =========================
        return Response({
            "summary": summary,
            "available_years": list(available_years),
            "selected_year": year,
            "usage_analytics": usage_analytics,
            "student_engagement": student_engagement
        })

