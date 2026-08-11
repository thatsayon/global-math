import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['DB_NAME'] = 'postgres'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASS'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
django.setup()

from administration.models import DailyChallenge, DailyChallengeTranslation
from post.models import PostModel, PostTranslation

challenges = DailyChallenge.objects.all().order_by('-publishing_date')
print("Total Challenges:", challenges.count())
for c in challenges[:2]:
    print(f"Challenge {c.id}: {c.name}")
    print("Translations:", c.translations.count())
    for t in c.translations.all():
        print(f"  [{t.language}] {t.translated_name}")
    print("Questions:")
    for q in c.questions.all():
        print(f"  Q: {q.question_text}")
        print("  Q Translations:", q.translations.count())

