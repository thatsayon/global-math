from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class UserAccount(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account'
    )
    # this field is for otp verification after login
    maf = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.user}"

class StudentProfile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    account = models.OneToOneField(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='student'
    )
    point = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.account.user} with {self.point}"


class StudentProgress(models.Model):
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    BASE_POINTS = 100  # tuning knob

    updated_at = models.DateTimeField(auto_now=True)

    def recalculate_level(self):
        self.level = max(
            1,
            int((self.total_points / self.BASE_POINTS) ** 0.5)
        )

    def add_points(self, points: int):
        self.total_points += points
        self.recalculate_level()
        self.save(update_fields=["total_points", "level", "updated_at"])


class DailyActivity(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="daily_activities"
    )
    date = models.DateField()
    points_earned = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("student", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student} | {self.date}"


class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # frontend icon key

    def __str__(self):
        return self.name


class EarnedBadge(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="earned_badges"
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "badge")

