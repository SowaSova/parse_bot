from django.db import models


class MediaType(models.TextChoices):
    PHOTO = "photo", "Фото"
    DOCUMENT = "document", "Документ"
    AUDIO = "audio", "Аудио"
    VIDEO = "video", "Видео"


class ButtonType(models.TextChoices):
    TEXT = "text", "Текстовая кнопка"
    CALLBACK = "callback", "Callback кнопка"
    URL = "url", "URL кнопка"
