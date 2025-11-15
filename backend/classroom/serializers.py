from rest_framework import serializers
from .models import (
    ClassroomMemberList,
    Classroom,
)

class CreateClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            'name',
            'description'
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
            "members_count"
        )

class JoinClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomMemberList
        fields = ["id", "user", "classroom", "joined_at"]
        read_only_fields = ["id", "joined_at"]

