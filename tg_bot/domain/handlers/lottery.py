from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.conf import settings

from apps.lottery.models import Lottery
from apps.users.models import TelegramUser

router = Router()


@router.callback_query(F.data.startswith("participate:"))
async def participate_callback(call: types.CallbackQuery):
    data = call.data.split(":")
    if len(data) != 2:
        return await call.answer("Неправильный формат данных", show_alert=True)
    lottery_id = data[1]

    # Получаем пользователя по telegram_id
    # Предполагается, что call.from_user.id - это telegram_id
    try:
        tg_user = await TelegramUser.objects.aget(telegram_id=call.from_user.id)
    except TelegramUser.DoesNotExist:
        # Нет такого пользователя в БД вообще, предложим перейти в бота
        await send_not_registered_message(call)
        return

    # Проверяем регистрацию (full_name и phone_number)
    if not tg_user.full_name or not tg_user.phone_number:
        await send_not_registered_message(call)
        return

    # Добавляем пользователя в участники лотереи
    try:
        lottery = await Lottery.objects.aget(id=lottery_id, is_finished=False)
        await lottery.participants.aadd(tg_user)
        await call.answer("Вы участвуете в розыгрыше!")
    except Lottery.DoesNotExist:
        await call.answer("Лотерея не найдена или уже завершена.", show_alert=True)


async def send_not_registered_message(call: types.CallbackQuery):
    # Кнопка-ссылка на бота для регистрации
    bot_username = settings.BOT_USERNAME
    link = f"https://t.me/{bot_username}?start=registration"
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Зарегистрироваться в боте", url=link)]
        ]
    )
    await call.message.answer(
        "Для участия в розыгрыше нужно зарегистрироваться в боте:", reply_markup=markup
    )
    await call.answer()
