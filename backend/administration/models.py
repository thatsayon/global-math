from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class LevelType(models.TextChoices):
    GENERAL = "general", "General Math Level"
    MEP = "mep", "MEP Math Level"

class MathLevels(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    level_type = models.CharField(
        max_length=20,
        choices=LevelType.choices,
        default=LevelType.GENERAL
    )


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

class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class SupportMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE) 
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class PointAdjustment(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    classroom_point = models.PositiveIntegerField(default=0)
    upvote_point = models.PositiveIntegerField(default=0)
    daily_challenge_point = models.PositiveIntegerField(default=0)


class DailyChallenge(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    name = models.CharField(max_length=255)
    description = models.TextField()

    subject = models.ForeignKey(
        MathLevels,
        on_delete=models.PROTECT,
        related_name="challenges"
    )
    grade = models.IntegerField()

    number_of_questions = models.PositiveIntegerField()
    points = models.PositiveIntegerField()

    image = models.ImageField(upload_to="challenges/", null=True, blank=True)

    publishing_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_translated_name(self, language):
        if not language or language == 'en':
            return self.name
        translation = self.translations.filter(language=language).first()
        return translation.translated_name if translation else self.name

    def get_translated_description(self, language):
        if not language or language == 'en':
            return self.description
        translation = self.translations.filter(language=language).first()
        return translation.translated_description if translation else self.description

class DailyChallengeTranslation(models.Model):
    challenge = models.ForeignKey(DailyChallenge, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10)
    translated_name = models.CharField(max_length=255)
    translated_description = models.TextField()

    class Meta:
        unique_together = ('challenge', 'language')

    def __str__(self):
        return f"{self.challenge.name} - {self.language}"

class ChallengeQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    challenge = models.ForeignKey(
        DailyChallenge,
        related_name="questions",
        on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField()

    question_text = models.TextField()
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Q{self.order}"

    def get_translated_question_text(self, language):
        if not language or language == 'en':
            return self.question_text
        translation = self.translations.filter(language=language).first()
        return translation.translated_question_text if translation else self.question_text

    def get_translated_answer(self, language):
        if not language or language == 'en':
            return self.answer
        translation = self.translations.filter(language=language).first()
        return translation.translated_answer if translation else self.answer

class ChallengeQuestionTranslation(models.Model):
    question = models.ForeignKey(ChallengeQuestion, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10)
    translated_question_text = models.TextField()
    translated_answer = models.CharField(max_length=255)

    class Meta:
        unique_together = ('question', 'language')

    def __str__(self):
        return f"Q{self.question.order} Translation - {self.language}"

class ActivityType(models.TextChoices):
    USER_REGISTERED = "user_registered", "User Registered"
    CLASSROOM_CREATED = "classroom_created", "Classroom Created"
    CHALLENGE_CREATED = "challenge_created", "Challenge Created"
    USER_BANNED = "user_banned", "User Banned"
    AI_QUESTION_CREATED = "ai_question_created", "AI Question Created"



class UserType(models.TextChoices):
    STUDENT = "student", "Student"
    TEACHER = "teacher", "Teacher"
    ADMIN = "admin", "Admin"
    USER = "user", "User"


class ActivityLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    affector_name = models.CharField(max_length=255)

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


