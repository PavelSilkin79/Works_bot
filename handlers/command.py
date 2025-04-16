import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row, Button, Column, Select, Multiselect
from sqlalchemy import select
from db import init_db
from config_data.config import load_config
from models import Organization, Installers, Welders
from states.states import CommandSG, OrgSG, InstallersSG, WeldersSG

command_router = Router()

async def setup_db():
    config = load_config()
    session_factory = await init_db(config)  # Получаем session_factory через init_db
    return session_factory

# Этот хэндлер будет срабатывать на команду /start
@command_router.message(CommandStart())
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать", callback_data="start_dialog")]
    ])
    await message.answer(
            '👋 Привет!Добро пожаловать в бота для управления организациями, монтажниками и сварщиками.\n'
            'Здесь ты можешь добавлять, редактировать и просматривать:\n'
            '🏢 Организации\n'
            '🛠 Монтажников\n'
            '🔧 Сварщиков\n'
        "Выбери действие ниже, чтобы начать 👇",
        reply_markup=keyboard
    )

@command_router.callback_query(F.data == "start_dialog")
async def launch_dialog(callback: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)
    await callback.answer()  # Чтобы убрать "часики"

@command_router.message(Command("help"))
async def help_command(message: Message):
    help_text = """
    Доступные команды:
    /start - начать работу с ботом (только для администратора)
    /help - показать это сообщение
    /list_organizations - 📒Список организаций
    /list_installers - 📒Список монтажников
    /list_welders - 📒Список сварщиков
    """
    await message.answer(help_text)

# Вывод всех организаций
@command_router.message(Command('list_organizations'))
async def list_organizations(message: Message, dialog_manager: DialogManager):
    session_factory = await setup_db()  # Получаем session_factory

    async with session_factory() as session:
        result = await session.execute(select(Organization))
        organizations = result.scalars().all()

    if not organizations:
        await message.answer('Организаций нет')
    else:
        text = "\n".join([f"{org.id}. {org.name} ({org.phone})" for org in organizations])
        await message.answer(f"Список организаций:\n{text}")

    await dialog_manager.start(state=OrgSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

@command_router.message(Command('list_installers'))
async def list_installers(message: Message, dialog_manager: DialogManager):
    session_factory = await setup_db()  # Получаем session_factory

    async with session_factory() as session:
        result = await session.execute(select(Installers))
        installers = result.scalars().all()

    if not installers:
        await message.answer('Монтажников нет')
    else:
        text = "\n".join([f"{inst.id}. {inst.name} ({inst.surname})" for inst in installers])
        await message.answer(f"Список монажников:\n{text}")

    await dialog_manager.start(state=InstallersSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})


@command_router.message(Command('list_welders'))
async def list_welders(message: Message, dialog_manager: DialogManager):
    session_factory = await setup_db()  # Получаем session_factory

    async with session_factory() as session:
        result = await session.execute(select(Welders))
        welders = result.scalars().all()

    if not welders:
        await message.answer('Сварщиков нет')
    else:
        text = "\n".join([f"{weld.id}. {weld.name} ({weld.surname})" for weld in welders])
        await message.answer(f"Список сварщиков:\n{text}")

    await dialog_manager.start(state=WeldersSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

async def check_and_start_org(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = await setup_db()  # Получаем session_factory

    async with session_factory() as session:
        result = await session.execute(select(Organization))
        organization = result.scalars().all()

        if not organization:
            # Сохраняем фабрику сессий для дальнейшего использования
            dialog_manager.dialog_data["session_factory"] = session_factory
            await dialog_manager.start(state=CommandSG.empty_organization, mode=StartMode.RESET_STACK)
        else:
            await dialog_manager.start(state=OrgSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

async def check_and_start_inst(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = await setup_db()  # Получаем session_factory

    async with session_factory() as session:
        result = await session.execute(select(Installers))
        installers = result.scalars().all()

        if not installers:
            # Сохраняем фабрику сессий для дальнейшего использования
            dialog_manager.dialog_data["session_factory"] = session_factory
            await dialog_manager.start(state=CommandSG.empty_installers, mode=StartMode.RESET_STACK)
        else:
            await dialog_manager.start(state=InstallersSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

async def check_and_start_welders(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = await setup_db()  # Получаем session_factory

    async with session_factory() as session:
        result = await session.execute(select(Welders))
        welders = result.scalars().all()

        if not welders:
            # Сохраняем фабрику сессий для дальнейшего использования
            dialog_manager.dialog_data["session_factory"] = session_factory
            await dialog_manager.start(state=CommandSG.empty_welders, mode=StartMode.RESET_STACK)
        else:
            await dialog_manager.start(state=WeldersSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})


# кнопки меню
async def go_add_org(callback: CallbackQuery, button, dialog_manager: DialogManager):
    session_factory = await setup_db()
    await dialog_manager.start(state=OrgSG.add_name, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

async def go_add_inst(callback: CallbackQuery, button, dialog_manager: DialogManager):
    session_factory = await setup_db()
    await dialog_manager.start(state=InstallersSG.add_name, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

async def go_add_welder(callback: CallbackQuery, button, dialog_manager: DialogManager):
    session_factory = await setup_db()
    await dialog_manager.start(state=WeldersSG.add_name, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})

async def go_back_main(callback: CallbackQuery, button, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)


add_dialog = Dialog(
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

command_router.include_router(add_dialog)