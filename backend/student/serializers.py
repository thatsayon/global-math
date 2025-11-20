from rest_framework import serializers
from django.contrib.auth import get_user_model

from administration.models import MathLevels

User = get_user_model()

class ProfileInformationSerializer(serializers.ModelSerializer):
    # Writeable by UUIDs
    math_levels = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MathLevels.objects.all(),
        write_only=True
    )
    # Read-only nested field for names in GET
    math_levels_info = serializers.SerializerMethodField(read_only=True)
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'profile_pic',
            'first_name',
            'last_name',
            'country',
            'math_levels',      # write-only for PATCH
            'math_levels_info', # read-only for GET
        )
        read_only_fields = ('id',)

    def get_math_levels_info(self, obj):
        return [{"id": level.id, "name": level.name} for level in obj.math_levels.all()]

    def update(self, instance, validated_data):
        # Handle math_levels separately
        math_levels = validated_data.pop('math_levels', None)
        if math_levels is not None:
            instance.math_levels.set(math_levels)
        return super().update(instance, validated_data)

