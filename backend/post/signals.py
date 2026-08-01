"""
Post-related badge signals.

Triggers:
  - first_question  → when a user creates their very first post
  - post_10         → when a user has created 10+ posts
  - post_50         → when a user has created 50+ posts
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PostModel


@receiver(post_save, sender=PostModel)
def check_post_badges(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    if not user:
        return

    # Only students get badges
    if not hasattr(user, 'account') or not hasattr(user.account, 'student'):
        return

    student = user.account.student

    from student.utils import award_badge_by_code

    # Count posts by this user (classroom=None means public posts)
    post_count = PostModel.objects.filter(user=user).count()

    if post_count == 1:
        award_badge_by_code(student, 'first_question')

    if post_count >= 10:
        award_badge_by_code(student, 'post_10')

    if post_count >= 50:
        award_badge_by_code(student, 'post_50')
