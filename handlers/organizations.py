from typing import Any
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select, SwitchTo
from aiogram_dialog.widgets.input import TextInput
from states import OrgSG, CommandSG
from utils import admin_required
from services.org_services import OrgServices


class OrgHandler:

    @staticmethod
    async def back_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

    @staticmethod
    async def start_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await OrgServices.handle_start_org_dialog(callback, dialog_manager)

    @staticmethod
    async def orgs_list(dialog_manager: DialogManager, **kwargs):
        return await OrgServices.get_organizations_list(dialog_manager)

    @staticmethod
    async def selected_org_data(dialog_manager: DialogManager, **kwargs):
        return await OrgServices.get_selected_org_data(dialog_manager)

    @staticmethod
    @admin_required
    async def add_org_name(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
        await OrgServices.handle_add_org_name(event, dialog_manager, text)

    @staticmethod
    async def add_org_address(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
        await OrgServices.handle_add_org_address(dialog_manager, text)

    @staticmethod
    async def add_org_phone(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
        await OrgServices.handle_add_org_phone(dialog_manager, text)

    @staticmethod
    async def add_org_email(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
        await OrgServices.handle_add_org_email(event, dialog_manager, text)

    @staticmethod
    @admin_required
    async def delete_selected_orgs(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await OrgServices.handle_delete_selected_orgs(callback, dialog_manager)

    @staticmethod
    @admin_required
    async def save_selected_org_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
        await OrgServices.handle_save_selected_org_id(dialog_manager, item_id)

    async def edit_org_field(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await OrgServices.handle_edit_org_field(button, dialog_manager)

    async def save_edited_field(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
        await OrgServices.handle_save_edited_field(event, dialog_manager, text)

    @staticmethod
    @admin_required
    async def save_info_org_id(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
        dialog_manager.dialog_data["organization_id"] = int(item_id)
        await dialog_manager.switch_to(OrgSG.show_org_info)