from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions

from django.db.models import Count
from django.shortcuts import get_object_or_404

from classroom.models import (
    Classroom,
    ClassRoomChallenge,
    QuestionOptions,
)
from post.serializers import PostFeedSerializer
from post.models import PostModel

from .serializers import (
    ClassRoomListSerializer,
    ClassRoomChallengeSerializer,
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
    queryset = Classroom.objects.annotate(
        post_count = Count('posts')
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
    queryset = ClassRoomChallenge.objects.all()

class AttendChallengeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, challenge_id):
        challenge = get_object_or_404(ClassRoomChallenge, id=challenge_id)

        attend, created = ChallengeAttend.objects.get_or_create(
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
        attend = get_object_or_404(
            ChallengeAttend,
            challenge_id=challenge_id,
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
            return Response({
                "is_complete": True,
                "message": "Challenge finished"
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

    def post(self, request, challenge_id, question_id):

        # 1. Verify student attended the challenge
        attend = get_object_or_404(
            ChallengeAttend,
            challenge_id=challenge_id,
            student=request.user
        )

        # 2. Ensure progress exists
        progress, _ = ChallengeProgress.objects.get_or_create(attend=attend)

        # 3. Get the question (ensures it belongs to this challenge)
        question = get_object_or_404(
            ChallengeQuestion,
            id=question_id,
            challenge_id=challenge_id
        )

        # 4. Validate option
        option_id = request.data.get("option_id")
        if not option_id:
            return Response({
                "error": "option_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        option = get_object_or_404(QuestionOptions, id=option_id)

        # Ensure option belongs to this question
        if option.question_id != question.id:
            return Response({
                "error": "This option does not belong to this question."
            }, status=400)

        # 5. Prevent answering out of order
        if question.order != progress.current_order:
            return Response({
                "error": "You cannot answer this question yet.",
                "current_order": progress.current_order
            }, status=400)

        # 6. Prevent double-answering
        if StudentAnswer.objects.filter(progress=progress, question=question).exists():
            return Response({
                "error": "You have already answered this question."
            }, status=400)

        # 7. Record correct option (for response)
        correct_option = QuestionOptions.objects.get(
            question=question,
            is_correct=True
        )

        # 8. Save the answer
        StudentAnswer.objects.create(
            progress=progress,
            question=question,
            selected_option=option,
            is_correct=option.is_correct
        )

        # 9. Update correct answer count
        if option.is_correct:
            progress.total_correct += 1

        # 10. Compute total questions
        total_questions = question.challenge.questions.count()
        progress.total_questions = total_questions

        # 11. Move to the next question
        progress.current_order += 1

        # 12. Challenge completion logic
        if progress.current_order > total_questions:
            progress.is_complete = True
            progress.points_earned = progress.total_correct * 12
            progress.save()

            accuracy = round((progress.total_correct / total_questions) * 100)

            return Response({
                "is_complete": True,
                "points": progress.points_earned,
                "correct_answers": progress.total_correct,
                "total_questions": total_questions,
                "accuracy": f"{accuracy}%",
                "correct_answer": {
                    "id": correct_option.id,
                    "text": correct_option.option
                }
            })

        # 13. Save progress and return next question order
        progress.save()

        return Response({
            "is_complete": False,
            "next_order": progress.current_order,
            "correct_answers": progress.total_correct,
            "correct_answer": {
                "id": correct_option.id,
                "text": correct_option.option
            }
        })


class ChallengeResultView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, challenge_id):
        attend = get_object_or_404(
            ChallengeAttend,
            challenge_id=challenge_id,
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

