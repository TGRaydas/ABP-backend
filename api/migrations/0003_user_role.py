# Generated by Django 3.0.5 on 2021-09-26 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_session_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
    ]
