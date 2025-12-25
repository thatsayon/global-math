from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileTopSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()
    streak = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "country",
            "points",
            "streak",
            "badges",
            "accuracy",
        )

    # ---------- helpers ----------

    def _get_student(self, obj):
        try:
            return obj.account.student
        except AttributeError:
            return None

    # ---------- metrics ----------

    def get_points(self, obj):
        student = self._get_student(obj)
        return student.point if student else 0

    def get_badges(self, obj):
        student = self._get_student(obj)
        return student.earned_badges.count() if student else 0

    def get_streak(self, obj):
        student = self._get_student(obj)
        if not student:
            return 0

        dates = student.daily_activities.values_list("date", flat=True)
        if not dates:
            return 0

        dates = sorted(set(dates), reverse=True)

        streak = 0
        prev = None

        for d in dates:
            if prev is None or prev == d + timedelta(days=1):
                streak += 1
            else:
                break
            prev = d

        return streak

    def get_accuracy(self, obj):
        """
        Example definition:
        accuracy = total_points / (days_active * BASE_POINTS)
        """
        student = self._get_student(obj)
        if not student or not hasattr(student, "progress"):
            return 0.0

        days_active = student.daily_activities.count()
        if days_active == 0:
            return 0.0

        max_points = days_active * student.progress.BASE_POINTS
        accuracy = student.progress.total_points / max_points

        return round(accuracy * 100, 2)
