from aiogram.fsm.state import StatesGroup, State


class OrgSG(StatesGroup):
    start = State()
    info_org = State()
    show_org_info = State()
    add_name = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_org = State()
    select_field = State() # выберите поле
    edit_field = State() # поле для редактирования
    delete_org = State()