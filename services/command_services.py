#import os
#from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
#from aiogram.filters import Command, CommandStart
#from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
#from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row, Button, Column, Select, Multiselect
from sqlalchemy import select
#from db import init_db
#from config_data.config import load_config
from db import Organization, Installers, Welders
from states import CommandSG, OrgSG, InstallersSG, WeldersSG
from aiogram.types import TelegramObject
from utils.access import admin_required

class CommandServices:

    @staticmethod
    async def check_and_start_org(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")

        async with session_factory() as session:
            result = await session.execute(select(Organization))
            organization = result.scalars().all()

            if not organization:
            # Сохраняем фабрику сессий для дальнейшего использования
                dialog_manager.dialog_data["session_factory"] = session_factory
                await dialog_manager.start(state=CommandSG.empty_organization, mode=StartMode.RESET_STACK)
            else:
                await dialog_manager.start(state=OrgSG.start, mode=StartMode.RESET_STACK)

    @staticmethod
    async def check_and_start_inst(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")

        async with session_factory() as session:
            result = await session.execute(select(Installers))
            installers = result.scalars().all()

            if not installers:
            # Сохраняем фабрику сессий для дальнейшего использования
                dialog_manager.dialog_data["session_factory"] = session_factory
                await dialog_manager.start(state=CommandSG.empty_installers, mode=StartMode.RESET_STACK)
            else:
                await dialog_manager.start(state=InstallersSG.start, mode=StartMode.RESET_STACK)#, data={"session_factory": session_factory})

    @staticmethod
    async def check_and_start_welders(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")  # Получаем session_factory

        async with session_factory() as session:
            result = await session.execute(select(Welders))
            welders = result.scalars().all()

            if not welders:
            # Сохраняем фабрику сессий для дальнейшего использования
                dialog_manager.dialog_data["session_factory"] = session_factory
                await dialog_manager.start(state=CommandSG.empty_welders, mode=StartMode.RESET_STACK)
            else:
                await dialog_manager.start(state=WeldersSG.start, mode=StartMode.RESET_STACK)#, data={"session_factory": session_factory})


# кнопки меню
    @staticmethod
    async def go_add_org(callback: CallbackQuery, button, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")  # Получаем session_factory
        await dialog_manager.start(state=OrgSG.add_name, mode=StartMode.RESET_STACK)#, data={"session_factory": session_factory})

    @staticmethod
    async def go_add_inst(callback: CallbackQuery, button, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")  # Получаем session_factory
        await dialog_manager.start(state=InstallersSG.add_name, mode=StartMode.RESET_STACK)#, data={"session_factory": session_factory})

    @staticmethod
    async def go_add_welder(callback: CallbackQuery, button, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")  # Получаем session_factory
        await dialog_manager.start(state=WeldersSG.add_name, mode=StartMode.RESET_STACK)#, data={"session_factory": session_factory})

    @staticmethod
    async def go_back_main(callback: CallbackQuery, button, dialog_manager: DialogManager):
        await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)
