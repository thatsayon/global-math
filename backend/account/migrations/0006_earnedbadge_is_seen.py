from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_seed_badges'),
    ]

    operations = [
        migrations.AddField(
            model_name='earnedbadge',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
    ]
