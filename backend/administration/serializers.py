from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from post.models import PostModel

from .models import (
    RecentActivity,
    MathLevels,
    PointAdjustment,
    ActivityLog,
    DailyChallenge,
)
User = get_user_model()

class RecentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentActivity
        fields = (
            "id",
            "recent_activity",
            "created_at",
            "full_name",
            "role"
        )

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "title",
            "message",
            "affector_name",
            "user_type",
            "created_at",
        )


class OverViewSerializer(serializers.Serializer):
    total_user = serializers.SerializerMethodField()
    total_student = serializers.SerializerMethodField()
    total_teacher = serializers.SerializerMethodField()
    total_active_user = serializers.SerializerMethodField()
    total_banned_user = serializers.SerializerMethodField()
    recent_activities = serializers.SerializerMethodField()

    def get_total_user(self, obj):
        return User.objects.count()

    def get_total_student(self, obj):
        return User.objects.filter(role="student").count()

    def get_total_teacher(self, obj):
        return User.objects.filter(role="teacher").count()

    def get_total_active_user(self, obj):
        return User.objects.filter(is_active=True).count()

    def get_total_banned_user(self, obj):
        return User.objects.filter(is_banned=True).count()

    def get_recent_activities(self, obj):
        activities = (
            ActivityLog.objects
            .all()
            .order_by("-created_at")[:5]
        )

        return ActivityLogSerializer(activities, many=True).data

class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_banned",
            "date_joined",
            "last_login"
        )

class ModerationTopSerializer(serializers.Serializer):
    total_user = serializers.SerializerMethodField()
    total_active_user = serializers.SerializerMethodField()
    total_post = serializers.SerializerMethodField()
    total_challenge = serializers.SerializerMethodField()

    def get_total_challenge(self, obj):
        return 10

    def get_total_user(self, obj):
        return User.objects.count()

    def get_total_active_user(self, obj):
        return User.objects.filter(is_active=True).count()

    def get_total_post(self, obj):
        return PostModel.objects.all().count()

class ModerationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "role",
            "is_banned",
            "warning",
        )

class ModerationSerializer(serializers.Serializer):
    top = ModerationTopSerializer()
    users = ModerationUserSerializer(many=True)

class MathLevelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MathLevels
        fields = ("id", "name", "slug")

class AdminProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'profile_pic',
        ]

    def validate(self, attrs):
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")

        if first_name and not first_name.strip():
            raise serializers.ValidationError({"first_name": "First name cannot be empty."})

        if last_name and not last_name.strip():
            raise serializers.ValidationError({"last_name": "Last name cannot be empty."})

        return attrs

    def update(self, instance, validated_data):
        # Update first and last name directly
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)

        # Update profile picture
        if "profile_pic" in validated_data:
            instance.profile_pic = validated_data["profile_pic"]

        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class LevelAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MathLevels
        fields = (
            "id",
            "name",
            "slug"
        )
        read_only_fields = ("slug",)


class PointAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointAdjustment
        fields = (
            'id',
            'classroom_point',
            'upvote_point',
            'daily_challenge_point',
        )

class ChallengeGenerationSerializer(serializers.Serializer):
    dificulty_level = serializers.IntegerField()
    subject = serializers.CharField()
    number_of_question = serializers.IntegerField()


class ChallengeQuestionInputSerializer(serializers.Serializer):
    order = serializers.IntegerField(min_value=1)
    question_text = serializers.CharField()
    answer = serializers.CharField()

class ChallengeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()

    subject = serializers.PrimaryKeyRelatedField(
        queryset=MathLevels.objects.all()
    )

    grade = serializers.IntegerField()
    points = serializers.IntegerField()
    publishing_date = serializers.DateField()

    questions = ChallengeQuestionInputSerializer(many=True)


class DailyChallengeListSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.name', read_only=True)
    class Meta:
        model = DailyChallenge
        fields = (
            'id',
            'name',
            'description',
            'subject',
            'number_of_questions',
            'points',
            'publishing_date'
        )


class DailyChallengeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyChallenge
        fields = (
            "name",
            "description",
            "points",
            "publishing_date",
        )

    def validate_publishing_date(self, value):
        today = timezone.now().date()

        if value < today:
            raise serializers.ValidationError(
                "Publishing date cannot be in the past."
            )

        return value
