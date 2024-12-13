from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tg_bot.domain import keyboards as kb

router = Router()


@router.callback_query(
    F.data.in_(
        [
            "back_to_main",
        ]
    )
)
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_channels_main":
        await state.clear()
        await callback_query.message.edit_text(
            "Выберите необходимый вариант",
            reply_markup=kb.get_channels_keyboard(),
        )
