from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from .utils import generate_room_code

import uuid

User = get_user_model()


class Classroom(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="classrooms_created"
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    room_code = models.CharField(max_length=20, unique=True, blank=True)
    members_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Create slug if missing
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Classroom.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Create unique room code if missing
        if not self.room_code:
            code = generate_room_code(self.name)

            while Classroom.objects.filter(room_code=code).exists():
                code = generate_room_code(self.name)

            self.room_code = code

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClassroomMemberList(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="classroom_memberships")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="members")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "classroom")  

    def __str__(self):
        return f"{self.user} joined {self.classroom.name}"

class ClassRoomChallenge(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='challenge'
    )
    challenge_name = models.CharField()
    challenge_description = models.CharField()
    joined_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    time_left = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Challenge of {self.classroom.name}"

class ChallengeQuestion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    challenge = models.ForeignKey(
        ClassRoomChallenge,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question = models.CharField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order}. {self.question_text[:30]}"


class QuestionOptions(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    question = models.ForeignKey(
        ChallengeQuestion,
        on_delete=models.CASCADE,
        related_name='options'
    )
    option = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            existing_count = ChallengeOption.objects.filter(question=self.question).count()
            if existing_count >= 4:
                raise ValueError("Each question must have exactly 4 options.")

        if self.is_correct:
            if ChallengeOption.objects.filter(question=self.question, is_correct=True).exists():
                raise ValueError("Only one option can be correct.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.option_text}"

