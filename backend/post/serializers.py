from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from utils.slang_detector import detect_slang

from post.tasks import run_nudity_check, translate_post_task
from core.utils import translate_text

from administration.models import MathLevels

from .models import (
    PostModel,
    CommentModel
)

class PostSerializer(serializers.ModelSerializer):
    post_level = serializers.PrimaryKeyRelatedField(
        queryset=MathLevels.objects.all(),
        required=True
    )

    class Meta:
        model = PostModel
        fields = (
            "id", "user", "classroom",
            "text", "image", "video",
            "post_level", "is_verified",
            "created_at", "updated_at"
        )
        read_only_fields = (
            "id", "user", "is_verified",
            "created_at", "updated_at"
        )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        classroom = validated_data.pop('classroom', None)

        text = validated_data.get('text', '')
        is_slang = detect_slang(text)
        if is_slang:
            raise ValidationError({"msg": "Your post contains inappropriate language."})

        post = PostModel.objects.create(
            user=user, 
            classroom=classroom,
            **validated_data
        )

        run_nudity_check.delay(str(post.id))
        
        translate_post_task.delay(str(post.id))

        return post

class PostFeedSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    post_level_name = serializers.SerializerMethodField()

    class Meta:
        model = PostModel
        fields = (
            "id", "user", "text", "image",
            "full_name", "profile_pic",
            "likes", "user_reaction", "post_level",
            "post_level_name", "created_at"
        )

    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return None

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return obj.user.profile_pic.url
        return None


    def get_post_level_name(self, obj):
        if obj.post_level:
            return obj.post_level.name

    def get_text(self, obj):
        user_lang = self.context['request'].user.language or 'en'
        if user_lang == obj.language:
            return obj.text  # show original if same language

        translation = obj.translations.filter(language=user_lang).first()
        return translation.translated_text if translation else obj.text

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_likes(self, obj):
        return obj.reactions.filter(reaction='like').count()

    def get_user_reaction(self, obj):
        user = self.context.get('request').user
        reaction = obj.reactions.filter(user=user).first()
        return reaction.reaction if reaction else None


class CommentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = CommentModel
        fields = (
            "id",
            "text",
            "image",
            "created_at",
            "updated_at",
            "full_name",
            "profile_pic",
            "like_count",
            "dislike_count",
            "user_reaction",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "full_name",
            "profile_pic",
            "like_count",
            "dislike_count",
            "user_reaction",
        ) 

    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return None

    def get_profile_pic(self, obj):
        if obj.user and obj.user.profile_pic:
            return obj.user.profile_pic.url
        return None

    def get_like_count(self, obj):
        return obj.reactions.filter(reaction="like").count()

    def get_dislike_count(self, obj):
        return obj.reactions.filter(reaction="dislike").count()

    def get_user_reaction(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            reaction = obj.reactions.filter(user=user).first()
            return reaction.reaction if reaction else None
        return None

    def validate(self, data):
        """
        Ensure at least one field (text or image) is provided when creating a comment.
        """
        if self.instance is None:  # Only run during creation
            text = data.get("text")
            image = data.get("image")
            if not text and not image:
                raise serializers.ValidationError(
                    "A comment must contain text or an image."
                )
        return data

