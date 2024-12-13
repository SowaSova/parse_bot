from django.core.exceptions import ValidationError
from django.db import models


class SingletonModel(models.Model):
    """
    Абстрактная модель-синглтон.
    Гарантирует, что в БД будет существовать ровно один экземпляр.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Если уже есть запись в БД этой модели (кроме текущей),
        # то не разрешаем создать вторую.
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError(
                "Экземпляр этой модели уже существует. Повторное создание запрещено."
            )
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Возвращает существующий экземпляр или создаёт новый, если его ещё нет.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
