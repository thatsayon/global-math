from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileTopSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'country',
        )
