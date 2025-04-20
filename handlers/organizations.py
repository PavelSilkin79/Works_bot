from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Select, Multiselect, SwitchTo
from aiogram_dialog.widgets.input import TextInput
from sqlalchemy import select, delete, func
from models import Organization
from states.states import OrgSG, CommandSG


org_router = Router()


async def back_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start,mode=StartMode.RESET_STACK,)

# Стартовый командный хэндлер
async def start_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    await dialog_manager.start(
        state=OrgSG.start,
        mode=StartMode.RESET_STACK,
        data={"session_factory": session_factory}
    )
    dialog_manager.start_data = {"session_factory": session_factory}

async def orgs_list(dialog_manager: DialogManager, **kwargs):
    session_factory = dialog_manager.middleware_data.get("session_factory")

    if not session_factory:
        await dialog_manager.done("❗ Ошибка подключения к базе данных.")
        return {"organizations": []}  # Возвращаем пустой список вместо ошибки

    async with session_factory() as session:
        result = await session.execute(select(Organization))
        organizations = result.scalars().all()
        if not organizations:
            # Получаем объект сообщения или колбэка
            event = dialog_manager.event
            if hasattr(event, "message"):
                await event.message.answer("❗ Список организаций пуст. Возвращаемся в меню.")
            elif hasattr(event, "callback_query"):
                await event.callback_query.message.answer("❗ Список организаций пуст. Возвращаемся в меню.")

            await dialog_manager.start(CommandSG.start, mode=StartMode.RESET_STACK)
            return {}

        return {"organizations": organizations}

async def show_org_info(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    async with session_factory() as session:
        org_id = dialog_manager.dialog_data.get("organization_id")
        if not org_id:
            await c.answer("Организация не выбрана.", show_alert=True)
            return
        # Проверяем, что организация существует в базе данных
        org = await session.get(Organization, org_id)
        if not org:
            await c.answer("Организация не найдена.", show_alert=True)
            return

        info = (
            f"🏢 <b>{org.name}</b>\n"
            f"📞 Телефон: {org.phone}\n"
            f"📍 Адрес: {org.address}\n"
            f"✉️ Email: {org.email}"
        )
        await c.message.answer(info, parse_mode="HTML")

# Добавление организации
async def add_org_name(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    # Проверка на существование организации с таким названием
    session_factory = dialog_manager.middleware_data.get("session_factory")

    async with session_factory() as session:
        existing_org = await session.execute(
            Organization.__table__.select().where(func.lower(Organization.name) == text.lower())
        )
        existing_org = existing_org.scalars().first()

        if existing_org:
            # Организация с таким названием уже существует
            await event.answer(f"Организация с таким названием '{text}' уже существует.")
            await dialog_manager.done()
            return

    # Если организация не существует, сохраняем название в данных диалога
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.next()

async def add_org_address(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["address"] = text
    await dialog_manager.next()

async def add_org_phone(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["phone"] = text
    await dialog_manager.next()

async def add_org_email(event:Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    dialog_manager.dialog_data["email"] = text

    async with session_factory() as session:

        # Если организация не существует, добавляем новую
        new_org = Organization(
            name=dialog_manager.dialog_data["name"],
            phone=dialog_manager.dialog_data["phone"],
            address=dialog_manager.dialog_data["address"],
            email=dialog_manager.dialog_data["email"],
        )
        session.add(new_org)
        await session.commit()

    # Отправляем сообщение, что организация была добавлена
    await event.answer(f"Организация '{dialog_manager.dialog_data['name']}' успешно добавлена!")
    await dialog_manager.done()
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)


async def delete_selected_orgs(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")

    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    selected_orgs = dialog_manager.find("del_org_multi").get_checked()
    if not selected_orgs:
        await callback.answer("⚠ Вы не выбрали организации для удаления.")
        return

    # Преобразуем ID из строк в числа
    try:
        selected_orgs = list(map(int, selected_orgs))
    except ValueError:
        await callback.answer("⚠ Ошибка: Некорректный формат ID.")
        return

    async with session_factory() as session:
        await session.execute(delete(Organization).where(Organization.id.in_(selected_orgs)))
        await session.commit()

    await callback.answer("✅ Организации удалены!")
     # Обновляем данные вручную через restart
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start)


async def save_selected_org_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["edit_org_id"] = int(item_id)  # Сохраняем ID выбранной организации
    await dialog_manager.next()  # Переход к следующему шагу


# Редактирование организации
async def edit_org_field(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Получаем id кнопки, которая была нажата (например, "name", "phone", "address", "email")
    field = button.widget_id
    dialog_manager.dialog_data["edit_field"] = field  # Сохраняем поле, которое будем редактировать
    await dialog_manager.next()

async def save_edited_field(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    edit_field = dialog_manager.dialog_data.get("edit_field")
    edit_org_id = dialog_manager.dialog_data.get("edit_org_id")

    if not edit_field:
        await event.answer("Ошибка: Не выбран элемент для редактирования.")
        return

    if not edit_org_id:
        await event.answer("Ошибка: ID организации отсутствует.")
        return

    # Запрос на обновление в базе данных
    session_factory = dialog_manager.middleware_data.get("session_factory")
    async with session_factory() as session:
        result = await session.execute(select(Organization).where(Organization.id == edit_org_id))
        org = result.scalar_one_or_none()

        if org:
            setattr(org, edit_field, str(text))  # Редактируем нужное поле
            await session.commit()
            FIELD_NAMES = {
                "address": "Адрес",
                "phone": "Телефон",
                "email": "Email",
                "name": "Название организации",
            }
            field_label = FIELD_NAMES.get(edit_field, edit_field)
            await event.answer(
            f"✅ Поле *{field_label}* обновлено на: *{text}*",
            parse_mode="Markdown"
            )
        else:
            await event.answer("Ошибка: Организация не найдена.")

    await dialog_manager.done()
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start)

async def save_info_org_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    async with session_factory() as session:
        org = await session.get(Organization, int(item_id))
        if not org:
            await callback.message.answer("Организация не найдена.")
        else:
            text = (
                f"🏢 <b>{org.name}</b>\n"
                f"📞 Телефон: {org.phone}\n"
                f"📍 Адрес: {org.address}\n"
                f"✉️ Email: {org.email}"
            )
            await callback.message.answer(f"ℹ️ Информация об организации:\n{text}", parse_mode="HTML")

    # Возврат в меню организации
    await dialog_manager.start(state=CommandSG.start)


start_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Column(
            SwitchTo(Const("ℹ️ Информация об организации"), id="info_org", state=OrgSG.info_org),
            SwitchTo(Const("✅ Добавить"), id="add_name", state=OrgSG.add_name),
            SwitchTo(Const("📝 Редактировать"), id="select_org", state=OrgSG.select_org),
            SwitchTo(Const("❌ Удалить"), id="delete_org", state=OrgSG.delete_org),
            Button(Const("🔙 Назад"), id="back", on_click=back_command),
        ),
        state=OrgSG.start,
    ),
    Window(
        Const("Введите название организации:"),
        TextInput(id="name_input", on_success=add_org_name),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.add_name,
    ),
    Window(
        Const("Введите телефон организации:"),
        TextInput(id="phone_input", on_success=add_org_phone),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.add_phone,
    ),
    Window(
        Const("Введите адрес организации:"),
        TextInput(id="address_input", on_success=add_org_address),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.add_address,
    ),
    Window(
        Const("Введите email организации:"),
        TextInput(id="email_input", on_success=add_org_email),
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
        Button(Const("❌ Удалить выбранные"), id="confirm_delete", on_click=delete_selected_orgs),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.delete_org,
        getter=orgs_list,
    ),
    Window(
        Const("Выберите организацию для просмотра информации:"),
        Column(
            Select(
                Format("{item.name}"),  # Показываем название организации
                id="edit_org_info",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="organizations",
                on_click=save_info_org_id,  # Вызываем обработчик при выборе
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.info_org,
        getter=orgs_list,  # Загружаем список организаций
    ),
    Window(
        Const("Выберите организацию для редактирования:"),
        Column(
            Select(
                Format("{item.name}"),  # Показываем название организации
                id="edit_org_select",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="organizations",
                on_click=save_selected_org_id,  # Вызываем обработчик при выборе
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.start),
        state=OrgSG.select_org,
        getter=orgs_list,  # Загружаем список организаций
    ),
    Window(
        Const("Выберите, что редактировать:"),
        Column(
            Button(Const("Название"), id="name", on_click=edit_org_field),
            Button(Const("Телефон"), id="phone", on_click=edit_org_field),
            Button(Const("Адрес"), id="address", on_click=edit_org_field),
            Button(Const("Email"), id="email", on_click=edit_org_field),
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.select_org),
        state=OrgSG.select_field,
    ),
    Window(
        Const("Введите новое значение:"),
        TextInput(id="new_value_input", on_success=save_edited_field),
        SwitchTo(Const("🔙 Назад"), id="back", state=OrgSG.select_field),
        state=OrgSG.edit_field,
    ),
)

org_router.include_router(start_dialog)