"""
Challenge-related badge signals.

Triggers:
  - first_challenge    → when a student completes their very first challenge
  - challenges_10      → 10 completed challenges
  - challenges_50      → 50 completed challenges
  - challenges_100     → 100 completed challenges
  - perfect_score      → 100% score on any challenge (score == total questions)
  - scholar            → student reaches level 10
  - grand_scholar      → student reaches level 25
  - streak_7/10/30/100 → checked on challenge completion
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ChallengeAttempt


@receiver(post_save, sender=ChallengeAttempt)
def check_challenge_badges(sender, instance, created, **kwargs):
    # Only trigger on newly completed challenges
    if not instance.completed:
        return

    student = instance.student

    from student.utils import award_badge_by_code, calculate_streaks

    # ---- Challenge count badges ----
    completed_count = ChallengeAttempt.objects.filter(
        student=student,
        completed=True
    ).count()

    if completed_count >= 1:
        award_badge_by_code(student, 'first_challenge')
    if completed_count >= 10:
        award_badge_by_code(student, 'challenges_10')
    if completed_count >= 50:
        award_badge_by_code(student, 'challenges_50')
    if completed_count >= 100:
        award_badge_by_code(student, 'challenges_100')

    # ---- Perfect score badge ----
    # A challenge is "perfect" if the student got score equal to the number
    # of questions in the challenge (each correct answer = 1 point assumed)
    challenge = instance.challenge
    total_questions = challenge.questions.count()
    if total_questions > 0 and instance.score >= total_questions:
        award_badge_by_code(student, 'perfect_score')

    # ---- Streak badges ----
    from challenge.models import ChallengeAttempt as CA
    from django.db.models.functions import TruncDate
    from django.db.models import Value

    challenge_dates = list(
        CA.objects.filter(student=student, completed=True)
        .values_list('created_at', flat=True)
    )
    challenge_dates = [dt.date() for dt in challenge_dates]
    current_streak, _ = calculate_streaks(challenge_dates)

    if current_streak >= 7:
        award_badge_by_code(student, 'streak_7')
    if current_streak >= 10:
        award_badge_by_code(student, 'streak_10')
    if current_streak >= 30:
        award_badge_by_code(student, 'streak_30')
    if current_streak >= 100:
        award_badge_by_code(student, 'streak_100')

    # ---- Level badges ----
    try:
        progress = student.progress
        if progress.level >= 10:
            award_badge_by_code(student, 'scholar')
        if progress.level >= 25:
            award_badge_by_code(student, 'grand_scholar')
    except Exception:
        pass
