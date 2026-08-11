from django.core.management.base import BaseCommand
from administration.models import DailyChallenge
from administration.tasks import translate_challenge_task

class Command(BaseCommand):
    help = 'Translate all existing challenges'

    def handle(self, *args, **kwargs):
        challenges = DailyChallenge.objects.all()
        self.stdout.write(f"Found {challenges.count()} challenges. Translating...")
        for c in challenges:
            self.stdout.write(f"Translating challenge: {c.name}")
            translate_challenge_task(str(c.id))
        self.stdout.write(self.style.SUCCESS('Successfully translated all challenges'))
