from django.db import models

TG_URL = "https://t.me/"

NEWS_INTERVAL = 60  # минут


class MediaType(models.TextChoices):
    PHOTO = "photo", "Фото"
    DOCUMENT = "document", "Документ"
    AUDIO = "audio", "Аудио"
    VIDEO = "video", "Видео"


class ButtonType(models.TextChoices):
    TEXT = "text", "Текстовая кнопка"
    CALLBACK = "callback", "Callback кнопка"
    URL = "url", "URL кнопка"
