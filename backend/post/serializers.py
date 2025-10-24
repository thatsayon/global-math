from rest_framework import serializers

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
