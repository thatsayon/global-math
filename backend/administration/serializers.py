from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import (
    RecentActivity,
)

User = get_user_model()

class RecentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentActivity
        fields = (
            "id",
            "recent_activity",
            "created_at",
            "full_name",
            "role"
        )

class OverViewSerializer(serializers.Serializer):
    total_user = serializers.SerializerMethodField()

    def get_total_user(self, obj):
        return User.objects.all().count()
