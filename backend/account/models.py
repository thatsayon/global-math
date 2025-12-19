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
