# from rest_framework import serializers
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
#


# class ProfileTopSerializer(serializers.ModelSerializer):
#     points = serializers.SerializerMethodField()
#     streak = serializers.SerializerMethodField()
#     badges = serializers.SerializerMethodField()
#     accuracy = serializers.SerializerMethodField()
#     profile_pic = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = (
#             "id",
#             "profile_pic",
#             "first_name",
#             "last_name",
#             "country",
#             "points",
#             "streak",
#             "badges",
#             "accuracy",
#         )
#
#     def get_profile_pic(self, obj):
#         if obj.profile_pic:
#             return obj.profile_pic.url
#         return None 
#     # ---------- helpers ----------
#
#     def _get_student(self, obj):
#         try:
#             return obj.account.student
#         except AttributeError:
#             return None
#
#     # ---------- metrics ----------
#
#     def get_points(self, obj):
#         student = self._get_student(obj)
#         return student.point if student else 0
#
#     def get_badges(self, obj):
#         student = self._get_student(obj)
#         return student.earned_badges.count() if student else 0
#
#     def get_streak(self, obj):
#         student = self._get_student(obj)
#         if not student:
#             return 0
#
#         dates = student.daily_activities.values_list("date", flat=True)
#         if not dates:
#             return 0
#
#         dates = sorted(set(dates), reverse=True)
#
#         streak = 0
#         prev = None
#
#         for d in dates:
#             if prev is None or prev == d + timedelta(days=1):
#                 streak += 1
#             else:
#                 break
#             prev = d
#
#         return streak
#
#     def get_accuracy(self, obj):
#         """
#         Example definition:
#         accuracy = total_points / (days_active * BASE_POINTS)
#         """
#         student = self._get_student(obj)
#         if not student or not hasattr(student, "progress"):
#             return 0.0
#
#         days_active = student.daily_activities.count()
#         if days_active == 0:
#             return 0.0
#
#         max_points = days_active * student.progress.BASE_POINTS
#         accuracy = student.progress.total_points / max_points
#
#         return round(accuracy * 100, 2)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


class ProfileTopSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()
    streak = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "profile_pic",
            "first_name",
            "last_name",
            "country",
            "points",
            "streak",
            "badges",
            "accuracy",
        )

    # ---------- media ----------

    def get_profile_pic(self, obj):
        return obj.profile_pic.url if obj.profile_pic else None

    # ---------- helpers ----------

    def _get_student(self, obj):
        try:
            return obj.account.student
        except AttributeError:
            return None

    def _get_progress(self, student):
        try:
            return student.progress
        except AttributeError:
            return None

    # ---------- metrics ----------

    def get_points(self, obj):
        student = self._get_student(obj)
        progress = self._get_progress(student) if student else None
        return progress.total_points if progress else 0

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
        Accuracy = total_points / (days_active * BASE_POINTS)
        """
        student = self._get_student(obj)
        progress = self._get_progress(student) if student else None

        if not progress:
            return 0.0

        days_active = student.daily_activities.count()
        if days_active == 0:
            return 0.0

        max_points = days_active * progress.BASE_POINTS
        accuracy = progress.total_points / max_points

        return round(accuracy * 100, 2)

