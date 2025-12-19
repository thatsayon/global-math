from django.db import models

from account.models import StudentProfile
from administration.models import DailyChallenge, ChallengeQuestion
import uuid

class ChallengeAttempt(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="challenge_attempts"
    )
    challenge = models.ForeignKey(
        DailyChallenge,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    score = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "challenge")


class QuestionAttempt(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    attempt = models.ForeignKey(
        ChallengeAttempt,
        on_delete=models.CASCADE,
        related_name="question_attempts"
    )
    question = models.ForeignKey(
        ChallengeQuestion,
        on_delete=models.CASCADE
    )

    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

