from aiogram.fsm.state import StatesGroup, State


class WeldersSG(StatesGroup):
    start = State()
    info_weld = State()        # список монтажников
    show_weld_info = State()
    add_name = State()
    add_surname = State()
    add_patronymic = State()
    add_photo = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_weld = State()
    select_field_weld = State() # выберите поле
    edit_field_weld = State() # поле для редактирования
    delete_weld = State()