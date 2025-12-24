from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from post.models import PostModel
from administration.models import MathLevels, SupportMessage

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
        )
        read_only_fields = ('id',)

    def get_math_levels_info(self, obj):
        return [{"id": level.id, "name": level.name} for level in obj.math_levels.all()]

    def update(self, instance, validated_data):
        math_levels = validated_data.pop('math_levels', None)
        if math_levels is not None:
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

    class Meta:
        model = PostModel
        fields = (
            'id',
            'text',
            'image',
            'video',
            'language',
            'is_verified',
            'created_at',
        )

    def get_image(self, obj):
        return obj.image.url if obj.image else None

    def get_video(self, obj):
        return obj.video.url if obj.video else None


class OtherProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    latest_post = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'profile_pic',
            'latest_post',
        )

    def get_profile_pic(self, obj):
        return obj.profile_pic.url if obj.profile_pic else None

    def get_latest_post(self, obj):
        post = (
            obj.posts
            .filter()
            .order_by('-created_at')
            .first()
        )

        if not post:
            return None

        return LatestPostSerializer(post).data

