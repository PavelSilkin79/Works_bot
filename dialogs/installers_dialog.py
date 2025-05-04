from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Select, Multiselect, SwitchTo, Row
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia
from states import InstallersSG
from handlers.installers import (get_installer_data, inst_list, add_inst_photo, save_selected_inst_id, save_info_inst_id, add_inst_name,
   add_inst_surname, add_inst_patronymic, skip_photo, add_inst_phone, add_inst_address, delete_selected_inst, add_inst_email,
   inst_list, get_installer_data, save_edited_field, back_command, edit_inst_field)


inst_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Column(
            SwitchTo(Const("ℹ️ Информация о монтажнике"), id="info_inst", state=InstallersSG.info_inst),
            SwitchTo(Const("✅ Добавить монтажника"), id="name", state=InstallersSG.add_name),
            SwitchTo(Const("📝 Редактировать"), id="select_installers", state=InstallersSG.select_inst),
            SwitchTo(Const("❌ Удалить"), id="delete_installers", state=InstallersSG.delete_inst),
            Button(Const("🔙 Назад"), id="back", on_click=back_command),
        ),
        state=InstallersSG.start,
    ),

    Window(
        Const("Введите имя монтажника:"),
        TextInput(id="name_input", on_success=add_inst_name),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_name,
    ),
    Window(
        Const("Введите фамилию монтажника:"),
        TextInput(id="surname_input", on_success=add_inst_surname),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_surname,
    ),
    Window(
        Const("Введите отчество монтажника:"),
        TextInput(id="patronymic_input", on_success=add_inst_patronymic),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_patronymic,
    ),
    Window(
        Const("Пожалуйста, отправьте фото монтажника или нажмите «Пропустить»:"),
        MessageInput(add_inst_photo, content_types=["photo"]),
        Row(Button(Const("Пропустить"), id="skip_photo", on_click=skip_photo),),
        state=InstallersSG.add_photo,
    ),
    Window(
        Const("Введите телефон монтажника:"),
        TextInput(id="phone_input", on_success=add_inst_phone),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_phone,
    ),
    Window(
        Const("Введите адрес проживания монтажника:"),
       TextInput(id="address_input", on_success=add_inst_address),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_address,
    ),
    Window(
        Const("Введите email монтажника:"),
        TextInput(id="email_input", on_success=add_inst_email),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_email,
    ),
    Window(
        Const("Выберите монтажника для удаления:"),
        Column(
            Multiselect(
                checked_text=Format("{item.name} {item.surname} ✅"),  # Когда элемент выбран
                unchecked_text=Format("{item.name} {item.surname} ❌"),  # Когда элемент НЕ выбран
                id="del_inst_multi",
                item_id_getter=lambda item: item.id,  # Получаем ID элемента
                items="installers",
            )
        ),
        Button(Const("❌ Удалить выбранные"), id="delete_selected_installers", on_click=delete_selected_inst),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.delete_inst,
        getter=inst_list,
    ),
    Window(
        Const("Выберите монтажника для просмотра информации:"),  # Текст перед выбором монтажника
        Column(
            Select(
                Format("{item.name}"),
                id="edit_inst_info",
                item_id_getter=lambda item: str(item.id),
                items="installers",
                on_click=save_info_inst_id,
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.info_inst,
        getter=inst_list,
    ),
    Window(
        DynamicMedia(
            selector=lambda data: data.get("photo"),

        ),
        Format(
            "👤 <b>{installer.surname} {installer.name} {installer.patronymic}</b>\n"
            "📞 Телефон: {installer.phone}\n"
            "📍 Адрес: {installer.address}\n"
            "✉️ Email: {installer.email}"
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.show_inst_info,
        parse_mode="HTML",
        getter=get_installer_data,  # Передаем getter для получения данных
    ),
    Window(
        Const("Выберите монтажника для редактирования:"),
        Column(
            Select(
                Format("{item.name} {item.surname}"),  # Показываем имя и фамилию монтажника
                id="edit_inst_select",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="installers",
                on_click=save_selected_inst_id,  # Вызываем обработчик при выборе
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.select_inst,
        getter=inst_list,  # Загружаем список монтажников
    ),
    Window(
        Const("Выберите, что редактировать:"),
        Column(
            Button(Const("Имя"), id="name", on_click=edit_inst_field),
            Button(Const("Фамилия"), id="surname", on_click=edit_inst_field),
            Button(Const("Отчество"), id="patronymic", on_click=edit_inst_field),
            Button(Const("Телефон"), id="phone", on_click=edit_inst_field),
            Button(Const("Адрес"), id="address", on_click=edit_inst_field),
            Button(Const("Email"), id="email", on_click=edit_inst_field),
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.select_inst),
        state=InstallersSG.select_field_inst,
    ),
    Window(
        Const("Введите новое значение:"),
        TextInput(id="new_value_input", on_success=save_edited_field),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.select_field_inst),
        state=InstallersSG.edit_field_inst,
    ),
)
