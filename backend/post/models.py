from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from cloudinary.models import CloudinaryField

from classroom.models import Classroom
from administration.models import MathLevels

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
    language = models.CharField(
        max_length=10,
        choices=User.LANGUAGE_CHOICES,
        default='en',
        help_text="Original language of the post"
    )
    post_level = models.ForeignKey(
        MathLevels,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Select math topic or level"
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

class PostTranslation(models.Model):
    post = models.ForeignKey(PostModel, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10)
    translated_text = models.TextField()

    class Meta:
        unique_together = ('post', 'language')
        verbose_name = "Post Translation"
        verbose_name_plural = "Post Translations"

    def __str__(self):
        return f"{self.post.id} ({self.language})"

class PostReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    post = models.ForeignKey(
        PostModel, 
        on_delete=models.CASCADE, 
        related_name='reactions'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='post_reactions'
    )
    reaction = models.CharField(
        max_length=10, 
        choices=REACTION_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  
        verbose_name = "Post Reaction"
        verbose_name_plural = "Post Reactions"

    def __str__(self):
        return f"{self.user.username} {self.reaction}d {self.post.id}"

class CommentModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    post = models.ForeignKey(
        PostModel,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments"
    )
    text = models.TextField(
        blank=True,
        null=True,
        help_text="Comment text (optional if image/video present)"
    )
    image = CloudinaryField(
        "comment_image",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

    def clean(self):
        # Ensure at least one field is filled (text, image, or video)
        if not self.text and not self.image and not self.video:
            raise ValidationError("A comment must contain text, an image, or a video.")


class CommentReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    comment = models.ForeignKey(
        CommentModel,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_reactions'
    )
    reaction = models.CharField(
        max_length=10,
        choices=REACTION_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')
        verbose_name = "Comment Reaction"
        verbose_name_plural = "Comment Reactions"

    def __str__(self):
        return f"{self.user.username} {self.reaction}d comment {self.comment.id}"
