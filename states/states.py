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
    select_field = State() # выберите поле
    edit_field = State() # поле для редактирования
    delete_org = State()


class InstallersSG(StatesGroup):
    start = State()
    add_name = State()
    add_surname = State()
    add_patronymic = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_inst = State()
    select_field_inst = State() # выберите поле
    edit_field_inst = State() # поле для редактирования
    delete_inst = State()


class WeldersSG(StatesGroup):
    start = State()
    add_name = State()
    add_surname = State()
    add_patronymic = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_weld = State()
    select_field_weld = State() # выберите поле
    edit_field_weld = State() # поле для редактирования
    delete_weld = State()