from aiogram import BaseMiddleware
from aiogram.types import Update

from tg_bot.domain.services import get_or_create_user


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        user = None

        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        else:
            return await handler(event, data)

        tg_id = user.id
        username = user.username

        user, created = await get_or_create_user(tg_id, username)

        data["user"] = user

        return await handler(event, data)
