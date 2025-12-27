from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Exists, OuterRef
from django.conf import settings

from account.models import StudentProfile, UserAccount, StudentProgress
from administration.models import DailyChallenge, ChallengeQuestion
from challenge.models import QuestionAttempt, ChallengeAttempt

from .ai_client import check_solution_with_ai
from .pagination import StandardResultsPagination, LeaderboardPagination

import os
import uuid

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


class JoinChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id):
        account = get_object_or_404(UserAccount, user=request.user)
        student = get_object_or_404(StudentProfile, account=account)
        challenge = get_object_or_404(DailyChallenge, id=challenge_id)

        attempt, created = ChallengeAttempt.objects.get_or_create(
            student=student,
            challenge=challenge
        )

        return Response(
            {
                "challenge_id": challenge.id,
                "status": "joined" if created else "already_joined"
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

class NextChallengeQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, challenge_id):
        account = get_object_or_404(UserAccount, user=request.user)
        student = get_object_or_404(StudentProfile, account=account)

        attempt = get_object_or_404(
            ChallengeAttempt,
            student=student,
            challenge_id=challenge_id
        )

        answered_qs = QuestionAttempt.objects.filter(
            attempt=attempt,
            question=OuterRef("pk")
        )

        question = (
            ChallengeQuestion.objects
            .filter(challenge_id=challenge_id)
            .annotate(answered=Exists(answered_qs))
            .filter(answered=False)
            .order_by("order")
            .first()
        )

        if not question:
            attempt.completed = True
            attempt.save(update_fields=["completed"])

            return Response(
                {
                    "status": "completed",
                    "challenge_score": attempt.score,
                    "total_questions": attempt.challenge.number_of_questions,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "question_id": str(question.id),
                "order": question.order,
                "question_text": question.question_text,
            },
            status=status.HTTP_200_OK
        )


def save_temp_file(file):
    upload_dir = os.path.join(settings.MEDIA_ROOT, "ai_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    name, ext = os.path.splitext(file.name)
    ext = ext.lower() or ".jpg"  # fallback, but extension SHOULD exist

    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    public_url = (
        f"{settings.BASE_URL}"
        f"{settings.MEDIA_URL}"
        f"ai_uploads/{filename}"
    )

    return file_path, public_url

class SubmitSolutionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # -----------------------------
        # Resolve student
        # -----------------------------
        account = get_object_or_404(UserAccount, user=request.user)
        student = get_object_or_404(StudentProfile, account=account)
        progress, _ = StudentProgress.objects.get_or_create(student=student)

        # -----------------------------
        # Validate question_id
        # -----------------------------
        question_id = request.data.get("question_id")
        if not question_id:
            return Response(
                {"detail": "question_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        question = get_object_or_404(ChallengeQuestion, id=question_id)
        challenge = question.challenge

        solution_text = request.data.get("solution_text")
        solution_image = request.FILES.get("solution_image")

        if not solution_text and not solution_image:
            return Response(
                {"detail": "Solution text or image is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # Get or create attempt
        # -----------------------------
        attempt, _ = ChallengeAttempt.objects.get_or_create(
            student=student,
            challenge=challenge
        )

        if attempt.completed:
            return Response(
                {"detail": "Challenge already completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent double answer
        if QuestionAttempt.objects.filter(
            attempt=attempt,
            question=question
        ).exists():
            return Response(
                {"detail": "Question already answered"},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_files = []
        solution_url = None

        try:
            # -----------------------------
            # Save image temporarily
            # -----------------------------
            if solution_image:
                file_path, solution_url = save_temp_file(solution_image)
                temp_files.append(file_path)

            # -----------------------------
            # AI evaluation
            # -----------------------------
            ai_result = check_solution_with_ai(
                problem_text=question.question_text,
                solution_text=solution_text,
                solution_url=solution_url,
            )

            is_correct = ai_result.get("status") == 0

            # -----------------------------
            # Save question attempt (STATE!)
            # -----------------------------
            QuestionAttempt.objects.create(
                attempt=attempt,
                question=question,
                is_correct=is_correct
            )

            # -----------------------------
            # Scoring
            # -----------------------------
            points_awarded = 0
            if is_correct and challenge.number_of_questions > 0:
                points_per_question = (
                    challenge.points // challenge.number_of_questions
                )

                attempt.score += points_per_question
                attempt.save(update_fields=["score"])

                progress.add_points(points_per_question)
                points_awarded = points_per_question

            # -----------------------------
            # Find next unanswered question
            # -----------------------------
            answered_qs = QuestionAttempt.objects.filter(
                attempt=attempt,
                question=OuterRef("pk")
            )

            next_question = (
                ChallengeQuestion.objects
                .filter(challenge=challenge)
                .annotate(answered=Exists(answered_qs))
                .filter(answered=False)
                .order_by("order")
                .first()
            )

            # -----------------------------
            # NEXT QUESTION
            # -----------------------------
            if next_question:
                return Response(
                    {
                        "status": "next_question",
                        "current": {
                            "question_id": str(question.id),
                            "order": question.order,
                            "correct": is_correct,
                            "points_awarded": points_awarded,
                        },
                        "next_question": {
                            "question_id": str(next_question.id),
                            "order": next_question.order,
                            "question_text": next_question.question_text,
                        },
                        "progress": {
                            "challenge_score": attempt.score,
                            "total_points": progress.total_points,
                            "level": progress.level,
                        }
                    },
                    status=status.HTTP_200_OK
                )

            # -----------------------------
            # CHALLENGE COMPLETED
            # -----------------------------
            attempt.completed = True
            attempt.save(update_fields=["completed"])

            total_questions = challenge.number_of_questions
            correct_answers = QuestionAttempt.objects.filter(
                attempt=attempt,
                is_correct=True
            ).count()

            return Response(
                {
                    "status": "completed",
                    "challenge": {
                        "id": str(challenge.id),
                        "name": challenge.name,
                        "total_questions": total_questions,
                        "correct_answers": correct_answers,
                        "points_earned": attempt.score,
                        "total_points_possible": challenge.points,
                    },
                    "progress": {
                        "level": progress.level,
                        "total_points": progress.total_points,
                    }
                },
                status=status.HTTP_200_OK
            )

        finally:
            for path in temp_files:
                try:
                    os.remove(path)
                except Exception:
                    pass

# class SubmitSolutionView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def post(self, request, challenge_id):
#         # -----------------------------
#         # Resolve student & challenge
#         # -----------------------------
#         account = get_object_or_404(UserAccount, user=request.user)
#         student = get_object_or_404(StudentProfile, account=account)
#         progress, _ = StudentProgress.objects.get_or_create(student=student)
#         challenge = get_object_or_404(DailyChallenge, id=challenge_id)
#
#         problem_text = request.data.get("problem_text")
#         solution_text = request.data.get("solution_text")
#
#         problem_image = request.FILES.get("problem_image")
#         solution_image = request.FILES.get("solution_image")
#
#         problem_url = None
#         solution_url = None
#         temp_files = []
#
#         try:
#             # -----------------------------
#             # Save images temporarily
#             # -----------------------------
#             if problem_image:
#                 path = save_temp_file(problem_image)
#                 temp_files.append(path)
#                 problem_url = f"file://{path}"
#
#             if solution_image:
#                 path = save_temp_file(solution_image)
#                 temp_files.append(path)
#                 solution_url = f"file://{path}"
#
#             # -----------------------------
#             # Validate input
#             # -----------------------------
#             if not problem_text and not problem_url:
#                 return Response(
#                     {"detail": "Problem text or image is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             if not solution_text and not solution_url:
#                 return Response(
#                     {"detail": "Solution text or image is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             # -----------------------------
#             # Call AI (single source of truth)
#             # -----------------------------
#             ai_result = check_solution_with_ai(
#                 problem_text=problem_text,
#                 solution_text=solution_text,
#                 problem_url=problem_url,
#                 solution_url=solution_url,
#             )
#
#             is_correct = ai_result.get("status") == 0
#
#             # -----------------------------
#             # Award challenge-based points
#             # -----------------------------
#             points_awarded = 0
#             if is_correct and challenge.number_of_questions > 0:
#                 points_per_question = (
#                     challenge.points // challenge.number_of_questions
#                 )
#                 progress.add_points(points_per_question)
#                 points_awarded = points_per_question
#
#             # -----------------------------
#             # Final response
#             # -----------------------------
#             return Response(
#                 {
#                     "correct": is_correct,
#                     "points_awarded": points_awarded,
#                     "total_points": progress.total_points,
#                     "level": progress.level,
#                     "ai": {
#                         "correct_solution": ai_result.get("correct_solution"),
#                         "extracted_solution": ai_result.get("extracted_solution"),
#                     }
#                 },
#                 status=status.HTTP_200_OK
#             )
#
#         finally:
#             # -----------------------------
#             # Cleanup temp files ALWAYS
#             # -----------------------------
#             for path in temp_files:
#                 try:
#                     os.remove(path)
#                 except Exception:
#                     pass
#
