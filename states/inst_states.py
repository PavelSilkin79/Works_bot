from aiogram.fsm.state import StatesGroup, State


class InstallersSG(StatesGroup):
    start = State()
    info_inst = State()        # список монтажников
    show_inst_info = State()   # отображение выбранного монтажника
    add_name = State()
    add_surname = State()
    add_patronymic = State()
    add_photo = State()
    add_phone = State()
    add_address = State()
    add_email = State()
    select_inst = State()
    select_field_inst = State() # выберите поле
    edit_field_inst = State() # поле для редактирования
    delete_inst = State()