from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from utils.slang_detector import detect_slang

from .models import (
    PostModel
)

class PostSerializer(serializers.ModelSerializer):
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
        
        return post
