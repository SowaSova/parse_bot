import random

from django.db.models import Count

from apps.lottery.models import Lottery


def choose_winner(lottery_id: int):
    lottery = Lottery.objects.get(id=lottery_id)
    participants = lottery.participants.all()
    if participants.exists():
        winner = random.choice(list(participants))
        lottery.winner = winner
        lottery.is_finished = True
        lottery.save()
        return winner
    return None
