from asgiref.sync import sync_to_async

from apps.lottery.models import Lottery


@sync_to_async
def update_lottery_participants(lottery_id: int, user_id: int):
    lottery = Lottery.objects.get(id=lottery_id)
    lottery.participants.add(user_id)
    lottery.save()
    return lottery
