# Generated by Django 5.1.4 on 2024-12-16 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0003_alter_language_param_value"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newschannel",
            name="link",
            field=models.URLField(default=1, verbose_name="Ссылка на канал"),
            preserve_default=False,
        ),
    ]
