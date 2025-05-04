import os
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.enums import ParseMode, ContentType
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Button, Select, Multiselect, Row
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from sqlalchemy import select, delete, func
from db.models import Installers
from states import InstallersSG, CommandSG
from utils.access import admin_required


# Назад в меню
async def back_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

# Стартовый командный хэндлер
async def start_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    await dialog_manager.start(
        state=InstallersSG.start,
        mode=StartMode.RESET_STACK,
        data={"session_factory": session_factory}
    )
    dialog_manager.start_data = {"session_factory": session_factory}


async def inst_list(dialog_manager: DialogManager, **kwargs):
    session_factory = dialog_manager.middleware_data.get("session_factory")

    if not session_factory:
        await dialog_manager.done("❗ Ошибка подключения к базе данных.")
        return {"installers": []}  # Возвращаем пустой список вместо ошибки

    async with session_factory() as session:
        result = await session.execute(select(Installers))
        installers = result.scalars().all()

        if not installers:
            await safe_send(dialog_manager, "❗ Список монтажников пуст. Возвращаемся в меню.")
            await dialog_manager.start(CommandSG.start, mode=StartMode.RESET_STACK)
            return {}
        return {"installers": installers}
        await dialog_manager.done()

# Добавление монтажника
@admin_required
async def add_inst_name(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.next()


async def add_inst_surname(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
     # Проверка на существование фамилии
    session_factory = dialog_manager.middleware_data.get("session_factory")

    async with session_factory() as session:
        existing_inst = await session.execute(
            select(Installers).where(func.lower(Installers.surname) == text.lower())
        )
        existing_inst = existing_inst.scalars().first()

        if existing_inst:
            # фамилия уже существует, прерываем выполнение
            await event.answer(f"Фамилия '{text}' уже существует.")
            return
            await dialog_manager.done()

    # Если фамилия  не существует, сохраняем название в данных диалога
    dialog_manager.dialog_data["surname"] = text
    await dialog_manager.next()

async def add_inst_patronymic (event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["patronymic"] = text
    await dialog_manager.next()

# Добавление фото
async def add_inst_photo(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото или нажмите «Пропустить».")
        return

        # Получаем файл с максимальным разрешением (последнее фото в списке)
    photo = message.photo[-1]

    file_id =  photo.file_id
    dialog_manager.dialog_data["photo_id"] = file_id
    await message.answer("Фото сохранено.")
    await dialog_manager.next()

async def add_inst_address(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["address"] = text
    await dialog_manager.next()

async def add_inst_phone(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["phone"] = text
    await dialog_manager.next()

async def add_inst_email(event:Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    dialog_manager.dialog_data["email"] = text

    async with session_factory() as session:
        new_installers= Installers(
            name=dialog_manager.dialog_data["name"],
            surname=dialog_manager.dialog_data["surname"],
            patronymic=dialog_manager.dialog_data["patronymic"],
            photo_id=dialog_manager.dialog_data["photo_id"],
            phone=dialog_manager.dialog_data["phone"],
            address=dialog_manager.dialog_data["address"],
            email=dialog_manager.dialog_data["email"],
        )
        session.add(new_installers)
        await session.commit()

    # Отправляем сообщение, что монтажник был добавлен
    await event.answer(f"Монтажник {dialog_manager.dialog_data['name']} {dialog_manager.dialog_data['surname']} успешно добавлен!")# надо добавить еще и фамилию
    await dialog_manager.done()
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

# Пропустить фото
async def skip_photo(c: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data["photo_id"] = None
    await c.answer("Фото пропущено.")
    await manager.next()

# Удаление монтажников
@admin_required
async def delete_selected_inst(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    selected_insts = dialog_manager.find("del_inst_multi").get_checked()
    if not selected_insts:
        await callback.answer("⚠ Вы не выбрали монтажников для удаления.")
        return

    # Преобразуем ID из строк в числа
    try:
        selected_insts = list(map(int, selected_insts))
    except ValueError:
        await callback.answer("⚠ Ошибка: Некорректный формат ID.")
        return

    async with session_factory() as session:
        await session.execute(delete(Installers).where(Installers.id.in_(selected_insts)))
        await session.commit()

    await callback.answer("✅ Монтажники удалены!")
     # Обновляем данные вручную через restart
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

# Выбор монтажника для редактирования
@admin_required
async def save_selected_inst_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["edit_inst_id"] = int(item_id)  # Сохраняем ID выбранного монтажника
    await dialog_manager.next()  # Переход к следующему шагу


# Редактирование данных монтажника
async def edit_inst_field(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Получаем id кнопки, которая была нажата (например, "name", "phone", "address", "email")
    field = button.widget_id
    dialog_manager.dialog_data["edit_field"] = field  # Сохраняем поле, которое будем редактировать
    await dialog_manager.next()

# Сохранение отредактированного значения
async def save_edited_field(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    edit_field = dialog_manager.dialog_data.get("edit_field")
    edit_inst_id = dialog_manager.dialog_data.get("edit_inst_id")

    if not edit_field:
        await event.answer("Ошибка: Не выбран элемент для редактирования.")
        return

    if not edit_inst_id:
        await event.answer("Ошибка: ID монтажник отсутствует.")
        return

    # Запрос на обновление в базе данных
    session_factory = dialog_manager.middleware_data.get("session_factory")
    async with session_factory() as session:
        result = await session.execute(select(Installers).where(Installers.id == edit_inst_id))
        inst = result.scalar_one_or_none()

        if inst:
            setattr(inst, edit_field, str(text))  # Редактируем нужное поле
            await session.commit()
            FIELD_NAMES = {
                "address": "Адрес",
                "phone": "Телефон",
                "email": "Email",
                "name": "Имя",
                "surname": "Фамилия",
                "patronymic": "Отчество",
                "photo_id": "Фото"
            }
            field_label = FIELD_NAMES.get(edit_field, edit_field)
            await event.answer(
            f"✅ Поле *{field_label}* обновлено на: *{text}*",
            parse_mode="Markdown"
            )
        else:
            await event.answer("Ошибка: Данные о монтажнике не найдена.")

    await dialog_manager.done()
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

@admin_required
async def save_info_inst_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    logging.info(f"Выбран монтажник с ID {item_id}")
    dialog_manager.dialog_data["installer_id"] = int(item_id)
    await dialog_manager.switch_to(InstallersSG.show_inst_info)

async def get_installer_data(dialog_manager: DialogManager, **kwargs):
    session_factory = dialog_manager.middleware_data["session_factory"]
    installer_id = dialog_manager.dialog_data.get("installer_id")

    async with session_factory() as session:
        inst = await session.get(Installers, installer_id)

        if not inst:
            return {"installer": None}

        return {
            "installer": inst,
            "photo": MediaAttachment(
                type=ContentType.PHOTO,
                file_id=MediaId(inst.photo_id),
            ) if inst.photo_id else None,
        }
