from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions

from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.db.models import (
    Q,
    Case,
    When,
    IntegerField,
    Count,
    FloatField,
    ExpressionWrapper,
    Sum,
)
from django.db import transaction


from classroom.models import (
    Classroom,
    ClassRoomChallenge,
    QuestionOptions,
    ClassroomMemberList,
)
from post.serializers import PostFeedSerializer
from post.models import PostModel

from .serializers import (
    ClassRoomListSerializer,
    ClassRoomChallengeSerializer,
    LeaderboardUserSerializer,
)
from .models import (
    ChallengeAttend,
    ChallengeProgress,
    StudentAnswer,
    ChallengeQuestion,
)
from .pagination import ClassroomFeedPagination

class ClassRoomListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassRoomListSerializer

    def get_queryset(self):
        user = self.request.user

        return (
            Classroom.objects
            .filter(members__user=user)          # 👈 ONLY joined classrooms
            .annotate(post_count=Count("posts"))
            .distinct()
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

    def get_queryset(self):
        classroom_id = self.kwargs.get('classroom_id')
        return ClassRoomChallenge.objects.filter(classroom_id=classroom_id)

class AttendChallengeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, challenge_id):
        challenge = get_object_or_404(ClassRoomChallenge, id=challenge_id)

        attend, created = ChallengeAttend.objects.get_or_create(
            classroom=challenge.classroom,
            challenge=challenge,
            student=request.user
        )

        if created:
            ChallengeProgress.objects.create(attend=attend)
            challenge.joined_count = challenge.joined_count + 1
            challenge.save()

        return Response({
            "message": "joined",
            "status": "new" if created else "already_joined"
        })

    def get(self, request, challenge_id):
        user = request.user

        challenge = get_object_or_404(
            ClassRoomChallenge,
            id=challenge_id
        )

        attend = get_object_or_404(
            ChallengeAttend,
            challenge_id=challenge_id,
            classroom=challenge.classroom,
            student=request.user
        )

        progress, _ = ChallengeProgress.objects.get_or_create(attend=attend)

        questions = attend.challenge.questions.order_by("order")
        total = questions.count()

        if total == 0:
            return Response({
                "error": "This challenge has no questions."
            }, status=400)

        if progress.is_complete:
            total_questions = progress.total_questions or attend.challenge.questions.count()

            accuracy = 0
            if total_questions > 0:
                accuracy = round((progress.total_correct / total_questions) * 100)

            return Response({
                "is_complete": True,
                "points": progress.points_earned,
                "correct_answers": progress.total_correct,
                "total_questions": total_questions,
                "accuracy": f"{accuracy}%"
            })

        if progress.current_order < 1:
            progress.current_order = 1
            progress.save()

        if progress.current_order > total:
            progress.is_complete = True
            progress.save()

            return Response({
                "is_complete": True,
                "message": "Challenge finished"
            })

        current_question = questions.filter(order=progress.current_order).first()

        if current_question is None:
            progress.current_order = 1
            progress.save()

            current_question = questions.first()

        return Response({
            "is_complete": False,
            "current_order": progress.current_order,
            "total_questions": total,
            "question": {
                "id": str(current_question.id),
                "text": current_question.question,
                "options": [
                    {"id": str(opt.id), "text": opt.option}
                    for opt in current_question.options.all()
                ]
            }
        })

class SubmitAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, challenge_id, question_id):
        user = request.user

        # 1. Fetch challenge
        challenge = get_object_or_404(
            ClassRoomChallenge,
            id=challenge_id
        )

        # 2. Fetch question (must belong to challenge)
        question = get_object_or_404(
            ChallengeQuestion,
            id=question_id,
            challenge=challenge
        )

        # 3. Verify attendance (challenge + classroom scoped)
        attend = get_object_or_404(
            ChallengeAttend,
            challenge=challenge,
            classroom=challenge.classroom,
            student=user
        )

        # 4. Ensure progress exists
        progress, _ = ChallengeProgress.objects.get_or_create(
            attend=attend
        )

        # 5. Block already completed challenge
        if progress.is_complete:
            return Response(
                {"error": "Challenge already completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 6. Validate option
        option_id = request.data.get("option_id")
        if not option_id:
            return Response(
                {"error": "option_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        option = get_object_or_404(
            QuestionOptions,
            id=option_id,
            question=question
        )

        # 7. Enforce strict order
        if question.order != progress.current_order:
            return Response(
                {
                    "error": "You cannot answer this question yet.",
                    "current_order": progress.current_order
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 8. Prevent double answer
        if StudentAnswer.objects.filter(
            progress=progress,
            question=question
        ).exists():
            return Response(
                {"error": "You already answered this question."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 9. Save answer
        StudentAnswer.objects.create(
            progress=progress,
            question=question,
            selected_option=option,
            is_correct=option.is_correct
        )

        # 10. Update progress counters
        if option.is_correct:
            progress.total_correct += 1

        total_questions = challenge.questions.count()
        progress.total_questions = total_questions

        # 11. Check completion (DETERMINISTIC)
        is_last_question = question.order == total_questions

        correct_option = QuestionOptions.objects.get(
            question=question,
            is_correct=True
        )

        if is_last_question:
            progress.is_complete = True
            progress.points_earned = progress.total_correct * 12
            progress.current_order = total_questions + 1

            # IMPORTANT: sync attend completion
            attend.is_complete = True
            attend.save(update_fields=["is_complete"])

            progress.save()

            accuracy = round(
                (progress.total_correct / total_questions) * 100
            )

            return Response({
                "is_complete": True,
                "points": progress.points_earned,
                "correct_answers": progress.total_correct,
                "total_questions": total_questions,
                "accuracy": f"{accuracy}%",
                "correct_answer": {
                    "id": str(correct_option.id),
                    "text": correct_option.option
                }
            })

        # 12. Move to next question
        progress.current_order += 1
        progress.save()

        return Response({
            "is_complete": False,
            "next_order": progress.current_order,
            "correct_answers": progress.total_correct,
            "correct_answer": {
                "id": str(correct_option.id),
                "text": correct_option.option
            }
        })

class ChallengeResultView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, challenge_id):
        attend = get_object_or_404(
            ChallengeAttend,
            challenge_id=challenge_id,
            classroom=attend.challenge.classroom,
            student=request.user
        )


        progress = attend.progress

        if not progress.is_complete:
            return Response({"error": "Challenge not completed"}, status=400)

        accuracy = round((progress.total_correct / progress.total_questions) * 100)

        return Response({
            "challenge_name": attend.challenge.challenge_name,
            "points": progress.points_earned,
            "correct_answers": progress.total_correct,
            "total_questions": progress.total_questions,
            "accuracy": f"{accuracy}%"
        })

class BrowserClassroomView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassRoomListSerializer

    def get_queryset(self):
        search = self.request.query_params.get("search", "").strip()

        qs = (
            Classroom.objects
            .annotate(
                post_count=Count("posts", distinct=True),
                member_count=Count("members", distinct=True),
                engagement_score=ExpressionWrapper(
                    (Count("posts") * 0.6) + (Count("members") * 0.4),
                    output_field=FloatField()
                )
            )
        )

        # 🔎 Apply search (optional)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            ).annotate(
                match_priority=ExpressionWrapper(
                    Case(
                        When(name__iexact=search, then=3),
                        When(name__icontains=search, then=2),
                        When(description__icontains=search, then=1),
                        default=0,
                        output_field=IntegerField()
                    ),
                    output_field=IntegerField()
                )
            ).order_by("-match_priority", "-engagement_score")


        # 🏆 Final ranking
        return qs.order_by("-engagement_score")


class JoinClassroomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        classroom_id = request.data.get("classroom_id")

        if not classroom_id:
            return Response(
                {"error": "classroom_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Get the classroom
        classroom = get_object_or_404(Classroom, id=classroom_id)

        user = request.user

        # 2. Check if already joined
        already_joined = ClassroomMemberList.objects.filter(
            user=user,
            classroom=classroom
        ).exists()

        if already_joined:
            return Response({
                "message": "You already joined this classroom."
            }, status=400)

        # 3. Create membership entry
        ClassroomMemberList.objects.create(
            user=user,
            classroom=classroom
        )

        # 4. Update classroom member count (optional but recommended)
        classroom.members_count = ClassroomMemberList.objects.filter(
            classroom=classroom
        ).count()
        classroom.save(update_fields=["members_count"])

        # 5. Response
        return Response({
            "message": "Joined classroom successfully.",
            "classroom_id": str(classroom.id),
            "classroom_name": classroom.name,
            "members": classroom.members_count
        }, status=201)

class JoinClassroomWithCode(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        room_code = request.data.get("room_code")

        if not room_code:
            return Response(
                {"error": "room_code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        room_code = room_code.strip()

        # ✅ FIX: use room_code field
        classroom = get_object_or_404(
            Classroom,
            room_code=room_code
        )

        if ClassroomMemberList.objects.filter(
            user=user,
            classroom=classroom
        ).exists():
            return Response(
                {"message": "You already joined this classroom."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ClassroomMemberList.objects.create(
            user=user,
            classroom=classroom
        )

        classroom.members_count = ClassroomMemberList.objects.filter(
            classroom=classroom
        ).count()
        classroom.save(update_fields=["members_count"])

        return Response(
            {
                "message": "Joined classroom successfully.",
                "classroom": {
                    "id": str(classroom.id),
                    "name": classroom.name,
                    "room_code": classroom.room_code,
                    "members": classroom.members_count,
                }
            },
            status=status.HTTP_201_CREATED
        )


class ClassroomLeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, classroom_id):
        user = request.user

        leaderboard_qs = (
            ChallengeProgress.objects
            .filter(
                attend__classroom_id=classroom_id,
                attend__is_complete=True
            )
            .values(
                "attend__student_id",
                "attend__student__first_name",
                "attend__student__last_name",
                "attend__student__username",
            )
            .annotate(
                total_points=Coalesce(Sum("points_earned"), 0)
            )
            .order_by("-total_points")
        )

        if not leaderboard_qs.exists():
            return Response(
                {"detail": "No leaderboard data yet."},
                status=status.HTTP_200_OK
            )

        leaderboard = []
        user_rank = None
        user_points = 0

        for index, row in enumerate(leaderboard_qs, start=1):
            full_name = (
                f"{row['attend__student__first_name']} "
                f"{row['attend__student__last_name']}"
            ).strip()

            display_name = full_name or row["attend__student__username"]

            leaderboard.append({
                "rank": index,
                "user_id": row["attend__student_id"],
                "name": display_name,
                "username": row["attend__student__username"],
                "points": row["total_points"],
            })

            if row["attend__student_id"] == user.id:
                user_rank = index
                user_points = row["total_points"]

        return Response(
            {
                "members": len(leaderboard),
                "your_rank": user_rank,
                "your_points": user_points,
                "top_users": leaderboard[:10]
            },
            status=status.HTTP_200_OK
        )
