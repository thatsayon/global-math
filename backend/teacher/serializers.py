from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.db import models 
from django.db import transaction

from classroom.models import (
    ClassroomMemberList, 
    ClassRoomChallenge,
    ChallengeQuestion,
    QuestionOptions,
    Classroom, 
)

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

# classroom related serializers

class ClassroomChallengeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoomChallenge
        fields = (
            'id',
            'challenge_name',
            'challenge_description',
            'points',
            'joined_count',
            'time_left',
            'created_at',
        )


class ClassroomChallengeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoomChallenge
        fields = (
            "id",
            "classroom",
            "challenge_name",
            "challenge_description",
            "points",
            "visibility",
        )
        read_only_fields = ("id",)

    def validate_classroom(self, classroom):
        request = self.context["request"]

        if classroom.creator != request.user:
            raise serializers.ValidationError(
                "You are not allowed to create challenges for this classroom."
            )

        return classroom



class QuestionOptionInputSerializer(serializers.Serializer):
    option = serializers.CharField(max_length=255)
    is_correct = serializers.BooleanField()


class QuestionWithOptionsCreateSerializer(serializers.Serializer):
    challenge = serializers.UUIDField()
    question = serializers.CharField()
    options = QuestionOptionInputSerializer(many=True)

    def validate(self, data):
        request = self.context["request"]

        # Validate challenge
        try:
            challenge = ClassRoomChallenge.objects.get(id=data["challenge"])
        except ClassRoomChallenge.DoesNotExist:
            raise serializers.ValidationError("Invalid challenge.")

        if challenge.classroom.creator != request.user:
            raise serializers.ValidationError(
                "You are not allowed to add questions to this challenge."
            )

        options = data["options"]

        if len(options) != 4:
            raise serializers.ValidationError(
                "Each question must have exactly 4 options."
            )

        correct_count = sum(1 for opt in options if opt["is_correct"])
        if correct_count != 1:
            raise serializers.ValidationError(
                "Exactly one option must be correct."
            )

        data["challenge_instance"] = challenge
        return data

    def create(self, validated_data):
        options_data = validated_data.pop("options")
        challenge = validated_data.pop("challenge_instance")

        # Auto order
        last_order = (
            ChallengeQuestion.objects
            .filter(challenge=challenge)
            .aggregate(max_order=models.Max("order"))
            .get("max_order") or 0
        )

        with transaction.atomic():
            question = ChallengeQuestion.objects.create(
                challenge=challenge,
                question=validated_data["question"],
                order=last_order + 1
            )

            for opt in options_data:
                QuestionOptions.objects.create(
                    question=question,
                    option=opt["option"],
                    is_correct=opt["is_correct"]
                )

        return question


class QuestionWithOptionsUpdateSerializer(serializers.Serializer):
    question = serializers.CharField()
    options = QuestionOptionInputSerializer(many=True)

    def validate(self, data):
        request = self.context["request"]
        question_obj = self.context["question"]

        if question_obj.challenge.classroom.creator != request.user:
            raise serializers.ValidationError(
                "You are not allowed to update this question."
            )

        # PATCH case: options not provided
        if "options" not in data:
            return data

        options = data["options"]

        if len(options) != 4:
            raise serializers.ValidationError(
                "Each question must have exactly 4 options."
            )

        correct_count = sum(1 for opt in options if opt["is_correct"])
        if correct_count != 1:
            raise serializers.ValidationError(
                "Exactly one option must be correct."
            )

        return data

    def update(self, instance, validated_data):
        options_data = validated_data.get("options")

        with transaction.atomic():
            if "question" in validated_data:
                instance.question = validated_data["question"]
                instance.save()

            if options_data is not None:
                instance.options.all().delete()
                for opt in options_data:
                    QuestionOptions.objects.create(
                        question=instance,
                        option=opt["option"],
                        is_correct=opt["is_correct"]
                    )

        return instance



class QuestionOptionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOptions
        fields = (
            "id",
            "option",
            "is_correct",   # ⚠️ teacher-only; hide later for students
        )


class ChallengeQuestionReadSerializer(serializers.ModelSerializer):
    options = QuestionOptionReadSerializer(many=True, read_only=True)

    class Meta:
        model = ChallengeQuestion
        fields = (
            "id",
            "question",
            "order",
            "options",
        )

