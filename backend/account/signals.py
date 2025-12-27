from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import UserAccount, StudentProfile, StudentProgress

User = get_user_model()


@receiver(post_save, sender=User)
def create_account_related_models(sender, instance, created, **kwargs):
    if not created:
        return

    # Atomic = either everything is created or nothing is
    with transaction.atomic():

        # Create account.UserAccount
        account = UserAccount.objects.create(
            user=instance,
            maf=False
        )

        # Only students get student-related models
        if instance.role == "student":
            student_profile = StudentProfile.objects.create(
                account=account
            )

            StudentProgress.objects.create(
                student=student_profile
            )

