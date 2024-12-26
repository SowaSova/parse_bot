from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.lottery.models import Lottery
from apps.lottery.tasks import announce_lottery, finish_lottery


@receiver(post_save, sender=Lottery)
def lottery_post_save(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: announce_lottery.delay(instance.pk))

        eta = instance.fin_date
        if eta > timezone.now():
            transaction.on_commit(
                lambda: finish_lottery.apply_async((instance.pk,), eta=eta)
            )
        else:
            transaction.on_commit(lambda: finish_lottery.delay(instance.pk))
