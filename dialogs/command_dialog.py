from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Select, Multiselect, SwitchTo, Row
from aiogram_dialog.widgets.input import TextInput
#from sqlalchemy import select, delete, func
from states import CommandSG
#from services.command_services import CommandServices
from handlers.command import (launch_dialog, check_and_start_org, check_and_start_inst, check_and_start_welders, go_add_org, go_back_main,
    go_add_welder, go_add_inst)


command_dialog = Dialog(
    Window(
        Const('Выбери действие ниже, чтобы начать 👇'),
        Column(
            Button(Const("✅ ОРГАНИЗАЦИИ"), id="org", on_click=check_and_start_org),
            Button(Const("✅ МОНТАЖНИКИ"), id="installers", on_click=check_and_start_inst),
            Button(Const("✅ СВАРЩИКИ"), id="welders", on_click=check_and_start_welders),
        ),
        state=CommandSG.start,
    ),
        Window(
        Const("❗ Список организаций пуст. Хотите добавить новую?"),
        Row(
            Button(Const("✅ Да"), id="add_org", on_click=go_add_org),
            Button(Const("🔙 Нет"), id="back_main", on_click=go_back_main),
        ),
        state=CommandSG.empty_organization,
    ),
    Window(
        Const("❗ Список сварщиков пуст. Хотите добавить нового?"),
        Row(
            Button(Const("✅ Да"), id="add_welder", on_click=go_add_welder),
            Button(Const("🔙 Нет"), id="back_main", on_click=go_back_main),
        ),
        state=CommandSG.empty_welders,
    ),
    Window(
        Const("❗ Список монтажников пуст. Хотите добавить нового?"),
        Row(
            Button(Const("✅ Да"), id="add_inst", on_click=go_add_inst),
            Button(Const("🔙 Нет"), id="back_main", on_click=go_back_main),
        ),
        state=CommandSG.empty_installers,
    )
)