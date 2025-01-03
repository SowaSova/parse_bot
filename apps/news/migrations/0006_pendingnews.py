# Generated by Django 5.1.4 on 2024-12-24 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0005_remove_newsfilter_country_remove_newsfilter_language_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PendingNews",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "news_id",
                    models.IntegerField(unique=True, verbose_name="ID новости"),
                ),
                ("title", models.CharField(max_length=500, verbose_name="Заголовок")),
                ("url", models.URLField(verbose_name="Ссылка на новость")),
                (
                    "posted",
                    models.BooleanField(default=False, verbose_name="Опубликовано"),
                ),
                (
                    "post_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Время публикации"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
