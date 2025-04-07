import os
from uuid import uuid4
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Button
from aiogram_dialog.widgets.input import TextInput
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import init_db, get_db
from config_data.config import load_config
from models import Installers
from states.states import InstallersSG, CommandSG

# Директория для сохранения фотографий
PHOTO_DIR = 'photos'
os.makedirs(PHOTO_DIR, exist_ok=True)

installers_router = Router()

async def setup_db():
    config: Config = load_config()
    session_factory = await init_db(config)
    return session_factory


async def back_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

# Добавление организации
async def add_inst_name(event: CallbackQuery, message: Message, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.next()

async def add_inst_address(event: CallbackQuery, message: Message, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["address"] = text
    await dialog_manager.next()

async def add_inst_phone(event: CallbackQuery, message: Message, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["phone"] = text
    await dialog_manager.next()

async def add_inst_email(event:Message, callback: CallbackQuery, dialog_manager: DialogManager, text: str):
    session_factory = await setup_db()
    dialog_manager.dialog_data["email"] = text

    async for session in get_db(session_factory):
        new_installers= Installers(
            name=dialog_manager.dialog_data["name"],
            phone=dialog_manager.dialog_data["phone"],
            address=dialog_manager.dialog_data["address"],
            email=dialog_manager.dialog_data["email"],
        )
        session.add(new_installers)
        await session.commit()

    # Отправляем сообщение, что организация была добавлена
    await event.answer(f"Монтажник '{dialog_manager.dialog_data['name']}' успешно добавлен!")
    await dialog_manager.done()
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

installers_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Column(
            SwitchTo(Const("✅ Добавить монтажника"), id="add_name", state=InstallersSG.add_name),
            SwitchTo(Const("📝 Редактировать"), id="select_installers", state=InstallersSG.select_installers),
            SwitchTo(Const("❌ Удалить"), id="delete_installers", state=InstallersSG.delete_installers),
            Button(Const("🔙 Назад"), id="back", on_click=back_command),
        ),
        state=InstallersSG.start,
    ),

    Window(
        Const("Введите ФИО монтажника:"),
        TextInput(id="name_input", on_success=add_inst_name),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_name,
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
)

installers_router.include_router(installers_dialog)