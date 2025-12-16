from django.db import models
from django.contrib.auth import get_user_model
from classroom.models import (
    ClassRoomChallenge,
    ChallengeQuestion,
    QuestionOptions,
)
import uuid

User = get_user_model()

class ChallengeAttend(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    classroom = models.ForeignKey(
        "classroom.Classroom",
        on_delete=models.CASCADE,
        related_name="challenge_attends"
    )
    challenge = models.ForeignKey(
        ClassRoomChallenge,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} attending {self.challenge}"


class ChallengeProgress(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    attend = models.OneToOneField(
        ChallengeAttend,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    current_order = models.PositiveIntegerField(default=1)
    is_complete = models.BooleanField(default=False)

    total_correct = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    points_earned = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.attend.student.username} progress"


class StudentAnswer(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    progress = models.ForeignKey(
        ChallengeProgress,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(ChallengeQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOptions, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_option.is_correct
        super().save(*args, **kwargs)
