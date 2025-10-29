from django.db import models
import uuid

class RecentActivity(models.Model):
    class RecentActivity(models.TextChoices):
        NEW_USER_CREATED = "new_user_created", "New User Created"
        USER_BANNED = "user_banned", "User Banned"
        ADMIN_LOGGED_IN = "admin_logged_in", "Admin Logged In"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    recent_activity = models.CharField(
        max_length=50,
        choices=RecentActivity.choices,
        help_text="Type of recent activity performed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField()
    role = models.CharField()

    def __str__(self):
        return f"{self.recent_activity}"

