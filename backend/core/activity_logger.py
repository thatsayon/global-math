from administration.models import ActivityLog, UserType


def log_user_registered(name: str):
    ActivityLog.objects.create(
        title="New user registered",
        message=f"{name} created a new account",
        affector_name=name,
        user_type=UserType.STUDENT,
    )


def log_classroom_created(teacher_name: str, classroom_name: str):
    ActivityLog.objects.create(
        title="New classroom created",
        message=f"{teacher_name} created classroom '{classroom_name}'",
        affector_name=teacher_name,
        user_type=UserType.TEACHER,
    )


def log_challenge_created(teacher_name: str, challenge_name: str):
    ActivityLog.objects.create(
        title="New challenge created",
        message=f"{teacher_name} created challenge '{challenge_name}'",
        affector_name=teacher_name,
        user_type=UserType.TEACHER,
    )


def log_user_banned(admin_name: str, banned_user_name: str):
    ActivityLog.objects.create(
        title="User banned",
        message=f"{banned_user_name} was banned",
        affector_name=admin_name,
        user_type=UserType.ADMIN,
    )


def log_ai_question_created(admin_name: str, question_title: str):
    ActivityLog.objects.create(
        title="AI question created",
        message=f"AI question '{question_title}' was created",
        affector_name=admin_name,
        user_type=UserType.ADMIN,
    )

