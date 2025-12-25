from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta

from account.models import (
    StudentProfile,
    DailyActivity,
    Badge,
    EarnedBadge,
)

def add_points(student: StudentProfile, points: int):
    today = timezone.now().date()

    activity, _ = DailyActivity.objects.get_or_create(
        student=student,
        date=today
    )
    activity.points_earned += points
    activity.save(update_fields=["points_earned"])

    student.progress.add_points(points)

def calculate_streaks(active_dates):
    active_dates = sorted(set(active_dates), reverse=True)

    current = 0
    longest = 0
    temp = 0
    prev = None

    for d in active_dates:
        if prev is None or prev == d + timedelta(days=1):
            temp += 1
        else:
            temp = 1

        longest = max(longest, temp)

        if prev is None:
            current = temp
        elif prev == d + timedelta(days=1) and current == temp - 1:
            current = temp

        prev = d

    return current, longest

def award_badge_by_code(student: StudentProfile, badge_code: str) -> bool:
    """
    Awards a badge to a student by badge code.

    Returns:
        True  -> badge was newly awarded
        False -> badge already existed or badge code invalid
    """

    try:
        with transaction.atomic():
            badge = Badge.objects.get(code=badge_code)

            EarnedBadge.objects.create(
                student=student,
                badge=badge
            )

            return True

    except Badge.DoesNotExist:
        # Invalid badge code
        return False

    except IntegrityError:
        # Badge already awarded (unique_together hit)
        return False

