from aiogram.fsm.state import StatesGroup, State


class CommandSG(StatesGroup):
    start = State()
    empty_organization = State()
    empty_welders = State()
    empty_installers = State()
