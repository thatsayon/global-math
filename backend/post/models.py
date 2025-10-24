from django.db import models
from django.contrib.auth import get_user_model

from cloudinary.models import CloudinaryField

from classroom.models import Classroom

import uuid

User = get_user_model()

class PostModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts"
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="posts",
        blank=True,
        null=True,
        help_text="The classroom this post belongs to"
    )
    text = models.TextField(
        blank=True,
        null=True,
        help_text="Math question or discussion text"
    )
    image = CloudinaryField(
        "post_image",
        blank=True,
        null=True
    )
    video = CloudinaryField(
        "post_video",
        resource_type="video",
        blank=True,
        null=True
    )
    post_level = models.PositiveSmallIntegerField(
        default=1,
        help_text="Math difficulty level (1=Easy, 2=Medium, 3=Hard)"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Indicates if the post is verified by AI"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return f"Post by {self.user} in {self.classroom} (Level {self.post_level})"
