from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_postnotinterested'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentmodel',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                help_text='If set, this comment is a reply to the referenced comment',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='replies',
                to='post.commentmodel',
            ),
        ),
        migrations.AlterModelOptions(
            name='commentmodel',
            options={
                'ordering': ['created_at'],
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
            },
        ),
    ]
