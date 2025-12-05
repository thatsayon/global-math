from rest_framework import serializers

from classroom.models import (
    Classroom,
    ClassRoomChallenge,
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
            'members_count',
            'description',
            'post_count'
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
