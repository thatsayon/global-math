from django.core.management.base import BaseCommand
from administration.models import MathLevels
from administration.tasks import translate_math_level_task

class Command(BaseCommand):
    help = 'Translates all existing math levels into target languages'

    def handle(self, *args, **kwargs):
        levels = MathLevels.objects.all()
        count = 0
        for level in levels:
            translate_math_level_task.delay(str(level.id))
            count += 1
            self.stdout.write(self.style.SUCCESS(f'Queued translation for: {level.name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully queued {count} math levels for translation'))
