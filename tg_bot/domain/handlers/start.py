import logging

from aiogram import F, Router
from aiogram.filters.command import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from django.utils.timezone import localtime

from apps.lottery.models import Lottery
from apps.users.models import TelegramUser
from tg_bot.domain import keyboards as kb
from tg_bot.domain.services.users import update_user
from tg_bot.domain.states import UserData

router = Router()

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message, state: UserData, user: TelegramUser):
    await state.clear()

    # Пытаемся получить параметр lottery_id из стартового параметра
    # Формат ожидается такой: /start lottery_123
    # где 123 - id розыгрыша
    lottery_id = None
    if message.text and " " in message.text:
        # message.text может быть "/start lottery_123"
        parts = message.text.strip().split(" ", 1)
        if len(parts) > 1 and parts[1].startswith("lottery_"):
            # Извлекаем id после "lottery_"
            try:
                lottery_id_str = parts[1].replace("lottery_", "")
                lottery_id = int(lottery_id_str)
            except ValueError:
                lottery_id = None

    # Если есть lottery_id, пытаемся получить соответствующий розыгрыш
    lottery = None
    if lottery_id is not None:
        try:
            lottery = await sync_to_async(Lottery.objects.get)(pk=lottery_id)
        except Lottery.DoesNotExist:
            lottery = None

    if lottery:
        from django.utils.timezone import now

        if lottery.is_finished or lottery.fin_date <= now():
            # Конкурс уже завершен или истёк
            await message.answer(
                f"Извините, розыгрыш «{lottery.title}» уже завершился!",
                reply_markup=await kb.get_main_keyboard(True),
            )
            return

    # Проверяем, зарегистрирован ли пользователь
    if user.registred:
        # Пользователь уже зарегистрирован
        if lottery is not None:
            # Добавляем пользователя в участники, если ещё не добавлен
            await sync_to_async(lottery.participants.add)(user)

            # Формируем сообщение о том, что он участвует
            fin_dt = localtime(lottery.fin_date).strftime("%d.%m.%Y %H:%M")
            await message.answer(
                f"Вы участвуете в розыгрыше «{lottery.title}»! Результаты будут объявлены {fin_dt}.",
                reply_markup=await kb.get_main_keyboard(True),
            )
        else:
            # Если никакой розыгрыш не указан - просто приветствуем
            await message.edit_text(
                "Привет и добро пожаловать!",
                reply_markup=await kb.get_main_keyboard(),
            )
    else:
        # Пользователь не зарегистрирован
        # Если есть розыгрыш - сохраняем его id в стейт, чтобы по завершении регистрации добавить
        if lottery is not None:
            await state.update_data(lottery_id=lottery_id)

        # Запускаем процесс регистрации
        sent_msg = await message.answer(
            "Привет и добро пожаловать!\nДавайте знакомиться, введите имя:"
        )
        await state.update_data(start_msg_id=sent_msg.message_id)
        await state.update_data(user_start_msg_id=message.message_id)
        await state.set_state(UserData.WaitForName)


@router.message(UserData.WaitForName)
async def get_name(message: Message, state: UserData):
    await state.update_data(name=message.text)
    data = await state.get_data()
    start_msg_id = data.get("start_msg_id")
    user_start_msg_id = data.get("user_start_msg_id")

    # Удаляем прошлые сообщения (бота и пользователя)
    if start_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, start_msg_id)
        except:
            pass
    if user_start_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, user_start_msg_id)
        except:
            pass

    # Сохраняем текущее пользовательское сообщение (с именем) для последующего удаления
    await state.update_data(user_name_msg_id=message.message_id)

    # Отправляем сообщение с просьбой отправить контакт
    sent_msg = await message.answer(
        "Отправьте контакт", reply_markup=kb.get_contact_keyboard()
    )
    # Сохраняем ID этого сообщения для удаления после получения контакта
    await state.update_data(contact_msg_id=sent_msg.message_id)
    await state.set_state(UserData.WaitForPhone)


@router.message(F.contact, UserData.WaitForPhone)
async def get_contact(message: Message, state: UserData, user: TelegramUser):
    data = await state.get_data()
    contact_msg_id = data.get("contact_msg_id")
    user_name_msg_id = data.get("user_name_msg_id")

    if contact_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, contact_msg_id)
        except:
            pass

    if user_name_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, user_name_msg_id)
        except:
            pass

    # Удаляем сообщение с контактом пользователя
    try:
        await message.bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    # Обновляем данные пользователя
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()

    try:
        await update_user(
            telegram_id=user.telegram_id,
            tg_username=user.tg_username,
            full_name=data.get("name"),
            phone_number=data.get("phone"),
        )
    except Exception as e:
        logger.error("Ошибка в обновлении пользователя: %s", e)
        # При ошибке просим заново ввести ФИО и убираем клавиатуру
        await message.answer(
            "Произошла ошибка, давайте попробуем ещё раз с ФИО: ",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(UserData.WaitForName)
        return
    finally:
        # Пользователь теперь зарегистрирован.
        lottery_id = data.get("lottery_id")
        await state.clear()
        mkup = await kb.get_main_keyboard(True)

        if lottery_id:
            # Пытаемся получить соответствующий розыгрыш
            lottery = await sync_to_async(Lottery.objects.filter(pk=lottery_id).first)()
            if lottery:
                await sync_to_async(lottery.participants.add)(user)
                fin_dt = localtime(lottery.fin_date).strftime("%d.%m.%Y %H:%M")
                await message.answer(
                    f"Спасибо за регистрацию! Теперь вы участвуете в розыгрыше «{lottery.title}»!\n"
                    f"Результаты будут объявлены {fin_dt}.",
                    reply_markup=mkup,
                )
                return

        # Если розыгрыша нет или не нашли
        await message.answer(
            "Спасибо за регистрацию! Теперь вы можете пользоваться ботом и участвовать в розыгрышах:",
            reply_markup=mkup,
        )
