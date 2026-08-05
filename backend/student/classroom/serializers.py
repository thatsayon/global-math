from rest_framework import serializers

from classroom.models import (
    Classroom,
    ClassRoomChallenge,
    JoinRequest
)
from post.models import PostModel

class ClassRoomListSerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField()

    class Meta:
        model = Classroom
        fields = (
            'id',
            'name',
            'slug',
            'room_code',
            'members_count',
            'description',
            'post_count',
            'is_public',
            'image'
        )


class ClassRoomChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoomChallenge
        fields = (
            'id',
            'challenge_name',
            'challenge_description',
            'joined_count',
            'time_left'
        )


class LeaderboardUserSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.UUIDField()
    name = serializers.CharField()
    points = serializers.IntegerField()

class StudentSentRequestsSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    classroom_image = serializers.SerializerMethodField()

    class Meta:
        model = JoinRequest
        fields = ["id", "classroom", "classroom_name", "classroom_image", "status", "created_at"]

    def get_classroom_image(self, obj):
        if obj.classroom.image:
            return obj.classroom.image.url
        return None
