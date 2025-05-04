from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Select, Multiselect, SwitchTo
from aiogram_dialog.widgets.input import TextInput
from states import OrgSG, CommandSG
from services.org_services import OrgServices
from handlers.organizations import OrgHandler


org_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Column(
            SwitchTo(Const("ℹ️ Информация об организации"), id="info_org", state=OrgSG.info_org),
            SwitchTo(Const("✅ Добавить"), id="add_name", state=OrgSG.add_name),
            SwitchTo(Const("📝 Редактировать"),  id="select_org",state=OrgSG.select_org),
            SwitchTo(Const("❌ Удалить"),  id="delete_org",state=OrgSG.delete_org),
            Button(Const("🔙 Назад"), id="back", on_click=OrgHandler.back_command),
        ),
        state=OrgSG.start,
    ),
    Window(
        Const("Введите название организации:"),
        TextInput(id="name_input", on_success=OrgHandler.add_org_name),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.add_name,
    ),
    Window(
        Const("Введите телефон организации:"),
        TextInput(id="phone_input", on_success=OrgHandler.add_org_phone),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.add_phone,
    ),
    Window(
        Const("Введите адрес организации:"),
        TextInput(id="address_input", on_success=OrgHandler.add_org_address),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.add_address,
    ),
    Window(
        Const("Введите email организации:"),
        TextInput(id="email_input", on_success=OrgHandler.add_org_email),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.add_email,
    ),
    Window(
        Const("Выберите организации для удаления:"),
        Column(
            Multiselect(
                checked_text=Format("{item.name} ✅"),  # Когда элемент выбран
                unchecked_text=Format("{item.name} ❌"),  # Когда элемент НЕ выбран
                id="del_org_multi",
                item_id_getter=lambda item: item.id,  # Получаем ID организации
                items="organizations",
            )
        ),
        Button(Const("❌ Удалить выбранные"), id="confirm_delete", on_click=OrgHandler.delete_selected_orgs),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.delete_org,
        getter=OrgHandler.orgs_list,
    ),
    Window(
        Const("Выберите организацию для просмотра информации:"),
        Column(
            Select(
                Format("{item.name}"),  # Показываем название организации
                id="edit_org_info",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="organizations",
                on_click=OrgHandler.save_info_org_id,  # Вызываем обработчик при выборе
            ),

        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.info_org,
        getter=OrgHandler.orgs_list,  # Загружаем список организаций
    ),
    Window(
        Format(
            "🏢 <b>{org.name}</b>\n"
            "📞 Телефон: {org.phone}\n"
            "📍 Адрес: {org.address}\n"
            "✉️ Email: {org.email}"
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.info_org),
    state=OrgSG.show_org_info,
    getter=OrgHandler.selected_org_data,
    ),
    Window(
        Const("Выберите организацию для редактирования:"),
        Column(
            Select(
                Format("{item.name}"),  # Показываем название организации
                id="edit_org_select",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="organizations",
                on_click=OrgHandler.save_selected_org_id,  # Вызываем обработчик при выборе
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.select_org,
        getter=OrgHandler.orgs_list,  # Загружаем список организаций
    ),
    Window(
        Const("Выберите, что редактировать:"),
        Column(
            Button(Const("Название"), id="name", on_click=OrgHandler.edit_org_field),
            Button(Const("Телефон"), id="phone", on_click=OrgHandler.edit_org_field),
            Button(Const("Адрес"), id="address", on_click=OrgHandler.edit_org_field),
            Button(Const("Email"), id="email", on_click=OrgHandler.edit_org_field),
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.select_org),
        state=OrgSG.select_field,
    ),
    Window(
        Const("Введите новое значение:"),
        TextInput(id="new_value_input", on_success=OrgHandler.save_edited_field),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.select_field),
        state=OrgSG.edit_field,
    ),
)