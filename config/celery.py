import os
from datetime import timedelta

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач в ваших приложениях
app.autodiscover_tasks()

from config.constants import NEWS_INTERVAL

app.conf.beat_schedule = {
    "parse-news-every-hour": {
        "task": "apps.news.tasks.parse_news_task",
        "schedule": timedelta(minutes=NEWS_INTERVAL),  # каждый час
    },
    "post-scheduled-news-every-minute": {
        "task": "apps.news.tasks.post_scheduled_news_task",
        "schedule": timedelta(minutes=1),  # каждую минуту
    },
    "remove-sended-news-every-day": {
        "task": "apps.news.tasks.remove_sended_news_task",
        "schedule": timedelta(days=1),  # каждый день
    },
}
