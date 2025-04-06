from aiogram.fsm.state import StatesGroup, State


class CommandSG(StatesGroup):
    start = State()


class OrgSG(StatesGroup):
    start = State()
    add_name = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_org = State()
    select_field = State()
    edit_field = State()
    delete_org = State()


class InstallersSG(StatesGroup):
    start = State()
    add_name = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_installers = State()
    delete_installers = State()


class WeldersSG(StatesGroup):
    start = State()
    add_name = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_welders = State()
    delete_welders = State()