from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0008_notification_fcm_metadata'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='postview',
            index=models.Index(
                fields=['user', 'post'],
                name='post_postview_user_post_idx',
            ),
        ),
    ]
