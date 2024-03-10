# Generated by Django 4.2 on 2024-03-06 01:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0015_topic_author'),
    ]

    operations = [
        migrations.RenameField(
            model_name='topic',
            old_name='user_created',
            new_name='user_created_topic',
        ),
        migrations.AlterField(
            model_name='topic',
            name='author',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
