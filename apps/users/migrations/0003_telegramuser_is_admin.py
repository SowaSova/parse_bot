# Generated by Django 5.1.4 on 2025-01-08 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_telegramuser_registred"),
    ]

    operations = [
        migrations.AddField(
            model_name="telegramuser",
            name="is_admin",
            field=models.BooleanField(default=False, verbose_name="Админ?"),
        ),
    ]
