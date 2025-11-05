from django.db import models
from django.utils.text import slugify
import uuid

class MathLevels(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while MathLevels.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

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

