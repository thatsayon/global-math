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
            'is_public'
        )

class ClassroomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            "id",
            "name",
            "description",
            "slug",
            "room_code",
            "members_count",
            "is_public"
        )

class JoinClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomMemberList
        fields = ["id", "user", "classroom", "joined_at"]
        read_only_fields = ["id", "joined_at"]

class JoinRequestSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = JoinRequest
        fields = ["id", "user", "classroom", "status", "created_at", "user_first_name", "user_last_name"]
        read_only_fields = ["id", "created_at"]

