from aiogram.fsm.state import State, StatesGroup


class UserData(StatesGroup):
    WaitForName = State()
    WaitForPhone = State()
