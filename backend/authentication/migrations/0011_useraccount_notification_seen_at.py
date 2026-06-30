from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_alter_useraccount_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='notification_seen_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
