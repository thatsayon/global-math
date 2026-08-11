import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from administration.models import DailyChallenge
from administration.tasks import translate_challenge_task

challenge = DailyChallenge.objects.last()
if challenge:
    print(f"Translating {challenge.id} ...")
    translate_challenge_task(challenge.id)
    print("Translations for JA:", challenge.translations.filter(language='ja').first())
