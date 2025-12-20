from rest_framework import serializers

from django.contrib.auth import get_user_model

from classroom.models import Classroom, ClassroomMemberList

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'username',
            'profile_pic',
            'gender',
            'language',
            'country',
        )


class MyClassroomSerializer(serializers.ModelSerializer):
    last_activity = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Classroom
        fields = (
            'id',
            'name',
            'slug',
            'room_code',
            'members_count',
            'last_activity'
        )

class ClassroomMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    profile_pic = serializers.CharField(source="user.profile_pic", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ClassroomMemberList
        fields = (
            "id",
            'first_name',
            'last_name',
            'profile_pic',
            "username",
            "email",
            "joined_at",
        )

class ClassroomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            'id',
            'name',
            'description',
            'room_code',
            'members_count'
        )
