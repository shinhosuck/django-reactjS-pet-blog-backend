# Generated by Django 4.2 on 2024-04-18 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0025_alter_post_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='like',
            new_name='likes',
        ),
    ]
