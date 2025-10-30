from rest_framework import serializers
from .models import (
    ClassroomMemberList
)

class JoinClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomMemberList
        fields = ["id", "user", "classroom", "joined_at"]
        read_only_fields = ["id", "joined_at"]

