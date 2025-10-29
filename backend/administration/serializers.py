from rest_framework import serializers

from django.contrib.auth import get_user_model

from post.models import PostModel

from .models import (
    RecentActivity,
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
        recent_activities = RecentActivity.objects.all().order_by('-created_at')[:5]
        serializer = RecentActivitySerializer(recent_activities, many=True)
        return serializer.data


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
            "date_joined"
        )

class ModerationTopSerializer(serializers.Serializer):
    total_user = serializers.SerializerMethodField()
    total_active_user = serializers.SerializerMethodField()
    total_post = serializers.SerializerMethodField()
    

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
