from asgiref.sync import sync_to_async
from django.db.models import Q

from apps.bot.models import FAQ, Manager
from config.constants import TG_URL


@sync_to_async
def get_manager_url():
    manager = Manager.load()
    return f"{TG_URL}{manager.tg_username}"


@sync_to_async
def get_faq(q: str = None):
    return list(FAQ.objects.filter(Q(question__icontains=q) | Q(answer__icontains=q)))
