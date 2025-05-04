from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Select, Multiselect, SwitchTo, Row
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia
from states import WeldersSG
from services.weld_services import WeldServices
from handlers.welders import (back_command, add_weld_name, add_weld_surname, add_weld_patronymic, add_weld_photo, add_weld_phone,
    add_weld_address, add_weld_email, delete_selected_weld, skip_photo, weld_list, save_info_weld_id, get_welders_data, save_selected_weld_id,
    edit_weld_field, save_edited_field)


weld_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Column(
            SwitchTo(Const("ℹ️ Информация о сварщике"), id="info_weld", state=WeldersSG.info_weld),
            SwitchTo(Const("✅ Добавить сварщика"), id="add_name", state=WeldersSG.add_name),
            SwitchTo(Const("📝 Редактировать"), id="select_welders", state=WeldersSG.select_weld),
            SwitchTo(Const("❌ Удалить"), id="delete_welders", state=WeldersSG.delete_weld),
            Button(Const("🔙 Назад"), id="back", on_click=back_command),
        ),
        state=WeldersSG.start,
    ),

    Window(
        Const("Введите имя сварщика:"),
        TextInput(id="name_input", on_success=add_weld_name),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_name,
    ),
        Window(
        Const("Введите фамилию сварщика:"),
        TextInput(id="surname_input", on_success=add_weld_surname),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_surname,
    ),
    Window(
        Const("Введите отчество сварщика:"),
        TextInput(id="patronymic_input", on_success=add_weld_patronymic),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_patronymic,
    ),
    Window(
        Const("Пожалуйста, отправьте фото монтажника или нажмите «Пропустить»:"),
        MessageInput(add_weld_photo, content_types=["photo"]),
        Row(Button(Const("Пропустить"), id="skip_photo", on_click=skip_photo),),
        state=WeldersSG.add_photo,
    ),
    Window(
        Const("Введите телефон сварщика:"),
        TextInput(id="phone_input", on_success=add_weld_phone),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_phone,
    ),
    Window(
        Const("Введите адрес проживания сварщика:"),
        TextInput(id="address_input", on_success=add_weld_address),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_address,
    ),
    Window(
        Const("Введите email сварщика:"),
        TextInput(id="email_input", on_success=add_weld_email),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_email,
    ),
    Window(
        Const("Выберите сварщика для удаления:"),
        Column(
            Multiselect(
                checked_text=Format("{item.name} {item.surname} ✅"),  # Когда элемент выбран
                unchecked_text=Format("{item.name} {item.surname} ❌"),  # Когда элемент НЕ выбран
                id="del_weld_multi",
                item_id_getter=lambda item: item.id,  # Получаем ID элемента
                items="welders",
            )
        ),
        Button(Const("❌ Удалить выбранные"), id="confirm_delete", on_click=delete_selected_weld),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.delete_weld,
        getter=weld_list,
    ),
    Window(
        Const("Выберите сварщика для просмотра информации:"),  # Текст перед выбором монтажника
        Column(
            Select(
                Format("{item.name}"),
                id="edit_weld_info",
                item_id_getter=lambda item: str(item.id),
                items="welders",
                on_click=save_info_weld_id,
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.info_weld,
        getter=weld_list,
    ),
    Window(
        DynamicMedia(
            selector=lambda data: data.get("photo"),
        ),
        Format(
            "👤 <b>{welder.surname} {welder.name} {welder.patronymic}</b>\n"
            "📞 Телефон: {welder.phone}\n"
            "📍 Адрес: {welder.address}\n"
            "✉️ Email: {welder.email}"
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.show_weld_info,
        parse_mode="HTML",
        getter=get_welders_data,  # Передаем getter для получения данных
    ),
    Window(
        Const("Выберите сварщика для редактирования:"),
        Column(
            Select(
                Format("{item.name} {item.surname}"),  # Показываем имя и фамилию
                id="edit_weld_select",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="welders",
                on_click=save_selected_weld_id,  # Вызываем обработчик при выборе
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.select_weld,
        getter=weld_list,  # Загружаем список сварщиков
    ),
    Window(
        Const("Выберите, что редактировать:"),
        Column(
            Button(Const("Имя"), id="name", on_click=edit_weld_field),
            Button(Const("Фамилия"), id="surname", on_click=edit_weld_field),
            Button(Const("Отчество"), id="patronymic", on_click=edit_weld_field),
            Button(Const("Телефон"), id="phone", on_click=edit_weld_field),
            Button(Const("Адрес"), id="address", on_click=edit_weld_field),
            Button(Const("Email"), id="email", on_click=edit_weld_field),
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.select_weld),
        state=WeldersSG.select_field_weld,
    ),
    Window(
        Const("Введите новое значение:"),
        TextInput(id="new_value_input", on_success=save_edited_field),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.select_field_weld),
        state=WeldersSG.edit_field_weld,
    ),
)