import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from sqlalchemy import select, delete, func
from db.models import Welders
from states import WeldersSG, CommandSG
from utils.access import admin_required


async def back_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

async def start_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return
    await dialog_manager.start(state=WeldersSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

async def weld_list(dialog_manager: DialogManager, **kwargs):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    if not session_factory:
        await dialog_manager.done("❗ Ошибка подключения к базе данных.")
        return {"welders": []}

    async with session_factory() as session:
        result = await session.execute(select(Welders))
        welders = result.scalars().all()
        if not welders:
            await dialog_manager.start(CommandSG.start, mode=StartMode.RESET_STACK)
            return {}
        return {"welders": welders}

@admin_required
async def add_weld_name(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.next()

async def add_weld_surname(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    async with session_factory() as session:
        existing = await session.execute(select(Welders).where(func.lower(Welders.surname) == text.lower()))
        if existing.scalars().first():
            await event.answer(f"Фамилия '{text}' уже существует.")
            await dialog_manager.done()
            return
    dialog_manager.dialog_data["surname"] = text
    await dialog_manager.next()

async def add_weld_patronymic(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["patronymic"] = text
    await dialog_manager.next()

async def add_weld_photo(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото или нажмите «Пропустить».")
        return
    dialog_manager.dialog_data["photo_id"] = message.photo[-1].file_id
    await message.answer("Фото сохранено.")
    await dialog_manager.next()

async def skip_photo(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data["photo_id"] = None
    await callback.answer("Фото пропущено.")
    await dialog_manager.next()

async def add_weld_address(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["address"] = text
    await dialog_manager.next()

async def add_weld_phone(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["phone"] = text
    await dialog_manager.next()

async def add_weld_email(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    dialog_manager.dialog_data["email"] = text

    async with session_factory() as session:
        weld = Welders(
            name=dialog_manager.dialog_data["name"],
            surname=dialog_manager.dialog_data["surname"],
            patronymic=dialog_manager.dialog_data["patronymic"],
            photo_id=dialog_manager.dialog_data["photo_id"],
            phone=dialog_manager.dialog_data["phone"],
            address=dialog_manager.dialog_data["address"],
            email=text,
        )
        session.add(weld)
        await session.commit()

    await event.answer(f"Сварщик {dialog_manager.dialog_data['name']} {dialog_manager.dialog_data['surname']} успешно добавлен!")
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

@admin_required
async def delete_selected_weld(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    selected = dialog_manager.find("del_weld_multi").get_checked()
    if not selected:
        await callback.answer("⚠ Вы не выбрали сварщика для удаления.")
        return
    try:
        selected_ids = list(map(int, selected))
    except ValueError:
        await callback.answer("⚠ Ошибка: Некорректный формат ID.")
        return

    async with session_factory() as session:
        await session.execute(delete(Welders).where(Welders.id.in_(selected_ids)))
        await session.commit()

    await callback.answer("✅ Сварщики удалены!")
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

@admin_required
async def save_selected_weld_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["edit_weld_id"] = int(item_id)
    await dialog_manager.next()

async def edit_weld_field(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data["edit_field"] = button.widget_id
    await dialog_manager.next()

async def save_edited_field(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    field = dialog_manager.dialog_data.get("edit_field")
    weld_id = dialog_manager.dialog_data.get("edit_weld_id")
    if not field or not weld_id:
        await event.answer("Ошибка: Не выбран элемент или ID сварщика.")
        return

    session_factory = dialog_manager.middleware_data.get("session_factory")
    async with session_factory() as session:
        weld = await session.get(Welders, weld_id)
        if weld:
            setattr(weld, field, text)
            await session.commit()
            names = {
                "address": "Адрес", "phone": "Телефон", "email": "Email",
                "name": "Имя", "surname": "Фамилия", "patronymic": "Отчество", "photo_id": "Фото"
            }
            await event.answer(f"✅ Поле *{names.get(field, field)}* обновлено на: *{text}*", parse_mode="Markdown")
        else:
            await event.answer("Ошибка: Данные о сварщике не найдены.")

    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

@admin_required
async def save_info_weld_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["welder_id"] = int(item_id)
    await dialog_manager.switch_to(WeldersSG.show_weld_info)

async def get_welders_data(dialog_manager: DialogManager, **kwargs):
    session_factory = dialog_manager.middleware_data["session_factory"]
    welder_id = dialog_manager.dialog_data.get("welder_id")
    async with session_factory() as session:
        weld = await session.get(Welders, welder_id)
        return {
            "welder": weld,
            "photo": MediaAttachment(
                type=ContentType.PHOTO,
                file_id=MediaId(weld.photo_id),
            ) if weld and weld.photo_id else None,
        }
