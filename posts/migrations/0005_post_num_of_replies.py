# Generated by Django 3.2 on 2024-01-08 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_topic_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='num_of_replies',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
