from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def delete_message(state: FSMContext, message: Message):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    if msg_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
