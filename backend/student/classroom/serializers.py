from rest_framework import serializers
from classroom.models import Classroom

class ClassRoomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            'id',
            'name',
            'slug',
            'members_count',
            'description'
        )
