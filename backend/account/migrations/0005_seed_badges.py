"""
Placeholder migration — no schema changes.
Run `python manage.py seed_badges` to seed badge data.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0004_badge_category"),
    ]

    operations = []
