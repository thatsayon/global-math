from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from post.models import PostModel
from administration.models import MathLevels, SupportMessage
from core.utils import get_translated_level_name
from account.models import (
    EarnedBadge,
)

User = get_user_model()

# profile serializers

class ProfileInformationSerializer(serializers.ModelSerializer):
    math_levels = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MathLevels.objects.all(),
        write_only=True
    )
    math_levels_info = serializers.SerializerMethodField(read_only=True)
    profile_pic = serializers.ImageField(required=False)
    level = serializers.SerializerMethodField(read_only=True)
    points = serializers.SerializerMethodField(read_only=True)
    badges = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'profile_pic',
            'first_name',
            'last_name',
            'country',
            'math_levels',      
            'math_levels_info', 
            'level',
            'points',
            'badges',
        )
        read_only_fields = ('id',)

    def get_math_levels_info(self, obj):
        return [{"id": level.id, "name": level.name, "level_type": level.level_type} 
                for level in obj.math_levels.all() if level.name.lower() != 'other']

    def get_level(self, obj):
        try:
            return obj.account.student.progress.level
        except AttributeError:
            return 1

    def get_points(self, obj):
        try:
            return obj.account.student.progress.total_points
        except AttributeError:
            return 0

    def get_badges(self, obj):
        try:
            student = obj.account.student
            earned = student.earned_badges.select_related('badge')
            return [
                {
                    "code": eb.badge.code,
                    "name": eb.badge.name,
                    "description": eb.badge.description,
                    "icon": eb.badge.icon,
                    "category": eb.badge.category,
                    "earned_at": eb.earned_at.isoformat()
                }
                for eb in earned
            ]
        except AttributeError:
            return []

    def update(self, instance, validated_data):
        math_levels = validated_data.pop('math_levels', None)
        if math_levels is not None:
            # Always ensure "Other" category is assigned
            other_level = MathLevels.objects.filter(name__iexact='Other').first()
            if other_level and other_level not in math_levels:
                math_levels.append(other_level)
            instance.math_levels.set(math_levels)
        return super().update(instance, validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=6)

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')

        if not old_password:
            raise serializers.ValidationError({"old_password": "This field is required."})
        if not new_password:
            raise serializers.ValidationError({"new_password": "This field is required."})
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})
        if old_password == new_password:
            raise serializers.ValidationError({"new_password": "New password must be different from old password"})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    send_by = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = (
            "id",
            "message",
            "sender",
            "sender_name",
            "send_by",
            "created_at"
        )
        read_only_fields = ("sender",)

    def get_send_by(self, obj):
        return "admin" if obj.sender.is_staff else "user"

class LatestPostSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    post_level_name = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    
    class Meta:
        model = PostModel
        fields = (
            'id',
            'user',
            'text',
            'image',
            'video',
            'language',
            'is_verified',
            'created_at',
            'post_level_name',
            'likes',
            'comment_count',
            'user_reaction',
        )

    def get_likes(self, obj):
        return obj.reactions.filter(reaction='like').count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            return reaction.reaction if reaction else None
        return None

    def get_post_level_name(self, obj):
        if obj.post_level:
            level_name = obj.post_level.name
            user_lang = self.context.get('request').user.language if self.context.get('request') and hasattr(self.context.get('request').user, 'language') else 'en'
            return get_translated_level_name(level_name, user_lang)
        return None

    def get_image(self, obj):
        return obj.image.url if obj.image else None

    def get_video(self, obj):
        return obj.video.url if obj.video else None



class OtherProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "profile_pic",
            "level",
            "points",
            "badges",
        )

    def get_profile_pic(self, obj):
        return obj.profile_pic.url if obj.profile_pic else None

    def get_level(self, obj):
        try:
            return obj.account.student.progress.level
        except AttributeError:
            return 1

    def get_points(self, obj):
        try:
            return obj.account.student.progress.total_points
        except AttributeError:
            return 0

    def get_badges(self, obj):
        try:
            student = obj.account.student
            earned = student.earned_badges.select_related('badge')
            return [
                {
                    "code": eb.badge.code,
                    "name": eb.badge.name,
                    "description": eb.badge.description,
                    "icon": eb.badge.icon,
                    "category": eb.badge.category,
                    "earned_at": eb.earned_at.isoformat()
                }
                for eb in earned
            ]
        except AttributeError:
            return []


# student activity serializers
class StudentProgressSerializer(serializers.Serializer):
    total_points = serializers.IntegerField()
    level = serializers.IntegerField()
    next_level_points = serializers.IntegerField()
    points_to_next_level = serializers.IntegerField()

class CalendarDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    points = serializers.IntegerField()
    active = serializers.BooleanField()

class EarnedBadgeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="badge.name")
    icon = serializers.CharField(source="badge.icon")
    code = serializers.CharField(source="badge.code")
    description = serializers.CharField(source="badge.description")
    category = serializers.CharField(source="badge.category")

    class Meta:
        model = EarnedBadge
        fields = ("name", "icon", "code", "description", "category", "earned_at")


class BadgeWithStatusSerializer(serializers.Serializer):
    """Serializes a badge along with whether the given student has earned it."""
    code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    category = serializers.CharField()
    earned = serializers.BooleanField()
    earned_at = serializers.DateTimeField(allow_null=True)


class StudentDashboardSerializer(serializers.Serializer):
    progress = StudentProgressSerializer()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    calendar = CalendarDaySerializer(many=True)
    badges = EarnedBadgeSerializer(many=True)




