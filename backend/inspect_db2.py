import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['DB_NAME'] = 'postgres'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASS'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['SECRET_KEY'] = 'fake_secret_key'

django.setup()

from administration.models import DailyChallenge, DailyChallengeTranslation
from account.models import UserAccount

challenges = DailyChallenge.objects.all().order_by('-publishing_date')
print(f"Total challenges: {challenges.count()}")
for c in challenges[:2]:
    print(f"Challenge ID: {c.id}")
    print(f"Name: {c.name}")
    print(f"Translations count: {c.translations.count()}")
    for t in c.translations.all():
        print(f"  [{t.language}] Name: {t.translated_name}")
    print("Questions:")
    for q in c.questions.all():
        print(f"  Q ID: {q.id}")
        print(f"  Q Text: {q.question_text}")
        print(f"  Q Translations count: {q.translations.count()}")
        for qt in q.translations.all():
            print(f"    [{qt.language}] Q Text: {qt.translated_question_text}")

users = UserAccount.objects.all()[:2]
for u in users:
    print(f"User {u.email} language: {u.language}")

