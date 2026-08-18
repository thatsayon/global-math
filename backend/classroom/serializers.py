from rest_framework import serializers
from .models import (
    ClassroomMemberList,
    Classroom,
    JoinRequest
)

class CreateClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            'name',
            'description',
            'is_public',
            'image'
        )

class ClassroomDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = (
            "id",
            "name",
            "description",
            "slug",
            "room_code",
            "members_count",
            "is_public",
            "image"
        )

    def get_image(self, obj):
        if obj.image:
            url = obj.image.url
            if 'res.cloudinary.com' in url and '/upload/' in url:
                if '/upload/v' in url:
                    return url.replace('/upload/v', '/upload/w_200,h_200,c_fill,q_auto,f_auto/v')
            return url
        return None

class JoinClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomMemberList
        fields = ["id", "user", "classroom", "joined_at"]
        read_only_fields = ["id", "joined_at"]

class JoinRequestSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = JoinRequest
        fields = ["id", "user", "classroom", "status", "created_at", "user_first_name", "user_last_name", "user_profile_pic"]
        read_only_fields = ["id", "created_at"]

    def get_user_profile_pic(self, obj):
        if obj.user.profile_pic:
            return obj.user.profile_pic.url
        return None

