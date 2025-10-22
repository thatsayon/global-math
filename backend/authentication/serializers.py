from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import get_user_model

import random
import string

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
            'profile_pic',
            'gender',
            'role',
            'language',
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def generate_unique_username(self, first_name, last_name):
        base = f"{first_name.lower()}-{last_name.lower()}" if first_name and last_name else "user"
        base = base.replace(" ", "-")

        while True:
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            username = f"{base}-{suffix}"
            if not User.objects.filter(username=username).exists():
                return username

    def create(self, validated_data):
        password = validated_data.pop('password')
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        # Generate random unique username
        username = self.generate_unique_username(first_name, last_name)

        user = User.objects.create(
            username=username,
            **validated_data
        )
        user.set_password(password)
        user.is_active = True  
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['profile_pic'] = user.profile_pic.url if user.profile_pic else 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png'
        return token
