from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0013_classroom_is_public_joinrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='classrooms/images/'),
        ),
    ]
