from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from account.models import StudentProfile, UserAccount
from administration.models import DailyChallenge
from challenge.models import QuestionAttempt, ChallengeAttempt

from .pagination import StandardResultsPagination, LeaderboardPagination

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # -----------------------------
        # Resolve student safely
        # -----------------------------
        account = get_object_or_404(UserAccount, user=request.user)
        student = get_object_or_404(StudentProfile, account=account)

        # -----------------------------
        # Leaderboard (Top 3 by POINT FIELD)
        # -----------------------------
        leaderboard_qs = (
            StudentProfile.objects
            .select_related("account__user")
            .order_by("-point")[:3]
        )

        leaderboard = [
            {
                "name": s.account.user.username,
                "points": s.point,
                "country": s.account.user.country
            }
            for s in leaderboard_qs
        ]

        # -----------------------------
        # User Rank (based on points)
        # -----------------------------
        ranked_ids = list(
            StudentProfile.objects
            .order_by("-point")
            .values_list("id", flat=True)
        )

        user_rank = ranked_ids.index(student.id) + 1 if student.id in ranked_ids else None

        # -----------------------------
        # Accuracy (safe even if empty)
        # -----------------------------
        total_questions = QuestionAttempt.objects.filter(
            attempt__student=student
        ).count()

        correct_answers = QuestionAttempt.objects.filter(
            attempt__student=student,
            is_correct=True
        ).count()

        accuracy = round(
            (correct_answers / total_questions) * 100, 2
        ) if total_questions > 0 else 0

        # -----------------------------
        # Challenges Attended
        # -----------------------------
        challenges_attended = ChallengeAttempt.objects.filter(
            student=student
        ).count()

        # -----------------------------
        # Daily Challenges List
        # -----------------------------
        challenges = DailyChallenge.objects.all().order_by("-publishing_date")

        challenge_data = []
        for c in challenges:
            attempt = ChallengeAttempt.objects.filter(
                student=student,
                challenge=c
            ).first()

            if not attempt:
                status = "new"
            elif attempt.completed:
                status = "completed"
            else:
                status = "in_progress"

            challenge_data.append({
                "id": c.id,
                "name": c.name,
                "subject": c.subject.name,
                "grade": c.grade,
                "points": c.points,
                "status": status
            })

        # -----------------------------
        # Final Response
        # -----------------------------
        return Response({
            "leaderboard": leaderboard,
            "user": {
                "total_points": student.point,
                "rank": user_rank,
                "accuracy": accuracy,
                "questions_attempted": total_questions,
                "challenges_attended": challenges_attended
            },
            "daily_challenges": challenge_data
        })



class ChallengeListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get(self, request):
        # -----------------------------
        # Resolve user + student
        # -----------------------------
        account = get_object_or_404(UserAccount, user=request.user)
        student = get_object_or_404(StudentProfile, account=account)

        # -----------------------------
        # Base queryset (recent → old)
        # -----------------------------
        queryset = DailyChallenge.objects.select_related(
            "subject"
        ).order_by("-publishing_date")

        # -----------------------------
        # Search system
        # -----------------------------
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(subject__name__icontains=search)
            )

        # -----------------------------
        # Pagination
        # -----------------------------
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        results = [
            {
                "id": c.id,
                "name": c.name,
                "subject": c.subject.name,
                "grade": c.grade,
                "points": c.points,
                "publishing_date": c.publishing_date,
            }
            for c in page
        ]

        # -----------------------------
        # Final paginated response
        # -----------------------------
        paginated_response = paginator.get_paginated_response(results)

        # Inject extra top-level data
        paginated_response.data["total_user_point"] = student.point

        return paginated_response


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get("period", "all_time")

        # -----------------------------
        # Base queryset (TOP 50 ONLY)
        # -----------------------------
        queryset = (
            StudentProfile.objects
            .select_related("account__user")
            .order_by("-point", "id")[:50]  # 🔒 hard limit
        )

        # -----------------------------
        # Build ranking list
        # -----------------------------
        ranked = []
        for idx, s in enumerate(queryset, start=1):
            user = s.account.user

            ranked.append({
                "rank": idx,
                "name": user.username,
                "country": user.country,
                "points": s.point,
                "profile_pic": user.profile_pic.url if user.profile_pic else None,
            })

        # -----------------------------
        # Split champions + global rankings
        # -----------------------------
        top_champions = ranked[:3]
        global_rankings = ranked[3:]

        # -----------------------------
        # Final response
        # -----------------------------
        return Response({
            "period": period,
            "top_champions": top_champions,
            "global_rankings": global_rankings,
            "total_returned": len(ranked)
        })
