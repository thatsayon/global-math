from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import get_user_model

from administration.models import MathLevels

import random
import string

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    math_levels = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MathLevels.objects.all(),
        required=False
    )

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
            'country',
            'math_levels',
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def generate_unique_username(self, first_name, last_name):
        import re
        first = first_name.strip().lower() if first_name else ""
        last = last_name.strip().lower() if last_name else ""

        if first and last:
            base = f"{first}_{last}"
        elif first:
            base = first
        elif last:
            base = last
        else:
            base = "user"

        # Replace spaces, hyphens with underscores, and strip other non-alphanumeric chars
        base = re.sub(r'[^a-z0-9_]', '', base.replace(" ", "_").replace("-", "_"))
        if not base:
            base = "user"

        # Truncate base to 25 characters to leave room for suffix up to 30 max length
        base = base[:25]

        # 1. Check if the base name itself is free
        if not User.objects.filter(username=base).exists():
            return base

        # 2. Try clean sequential suffixes (e.g. jamie_laprairie_2)
        for i in range(2, 100):
            username = f"{base}_{i}"
            if len(username) > 30:
                username = f"{base[:30 - len(str(i)) - 1]}_{i}"
            if not User.objects.filter(username=username).exists():
                return username

        # 3. Fallback to random digits if needed
        while True:
            suffix = ''.join(random.choices(string.digits, k=4))
            username = f"{base}_{suffix}"
            if len(username) > 30:
                username = f"{base[:25]}_{suffix}"
            if not User.objects.filter(username=username).exists():
                return username

    def create(self, validated_data):
        math_levels = validated_data.pop('math_levels', [])
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
        user.math_levels.set(math_levels)
        return user

class UpdateLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('language',)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['profile_pic'] = user.profile_pic.url if user.profile_pic else 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png'
        return token
