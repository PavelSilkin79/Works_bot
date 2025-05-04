from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select, SwitchTo
from sqlalchemy import select, delete, func
from utils.messaging import safe_send
from db import Organization
from states import OrgSG, CommandSG


class OrgServices:

    @staticmethod
    async def handle_start_org_dialog(callback: CallbackQuery, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")
        if not session_factory:
            await callback.answer("⚠ Ошибка: База данных недоступна.")
            return
        await dialog_manager.start(state=OrgSG.start, mode=StartMode.RESET_STACK, data={"session_factory": session_factory})
        dialog_manager.start_data = {"session_factory": session_factory}

    @classmethod
    async def get_organizations_list(cls, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")
        if not session_factory:
            return {"organizations": []}

        async with session_factory() as session:
            result = await session.execute(select(Organization))
            organizations = result.scalars().all()

            if not organizations:
                await safe_send(dialog_manager, "❗ Список организаций пуст. Возвращаемся в меню.")
                await dialog_manager.start(state=StartMode.RESET_STACK)
                return {}

            return {"organizations": organizations}
            await dialog_manager.done()


    @staticmethod
    async def get_selected_org_data(dialog_manager: DialogManager, **kwargs):
        session_factory = dialog_manager.middleware_data.get("session_factory")
        org_id = dialog_manager.dialog_data.get("organization_id")

        if not session_factory or not org_id:
            return {"org": None}

        async with session_factory() as session:
            org = await session.get(Organization, org_id)
            return {"org": org}

    @staticmethod
    async def handle_add_org_name(event: Message, dialog_manager: DialogManager, text: str):
        session_factory = dialog_manager.middleware_data.get("session_factory")
        async with session_factory() as session:
            existing_org = await session.execute(
                select(Organization).where(func.lower(Organization.name) == func.lower(text))
            )
            if existing_org.scalars().first():
                await event.answer(f"Организация с таким названием '{text}' уже существует.")
                await dialog_manager.done()
                return
        dialog_manager.dialog_data["name"] = text
        await dialog_manager.next()

    @staticmethod
    async def handle_add_org_address(dialog_manager: DialogManager, text: str):
        dialog_manager.dialog_data["address"] = text
        await dialog_manager.next()

    @staticmethod
    async def handle_add_org_phone(dialog_manager: DialogManager, text: str):
        dialog_manager.dialog_data["phone"] = text
        await dialog_manager.next()

    @staticmethod
    async def handle_add_org_email(event: Message, dialog_manager: DialogManager, text: str):
        session_factory = dialog_manager.middleware_data.get("session_factory")
        dialog_manager.dialog_data["email"] = text
        async with session_factory() as session:
            new_org = Organization(**dialog_manager.dialog_data)
            session.add(new_org)
            await session.commit()
        await event.answer(f"Организация '{dialog_manager.dialog_data['name']}' успешно добавлена!")
        await dialog_manager.done()
        await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

    @staticmethod
    async def handle_delete_selected_orgs(callback: CallbackQuery, dialog_manager: DialogManager):
        session_factory = dialog_manager.middleware_data.get("session_factory")
        selected_orgs = dialog_manager.find("del_org_multi").get_checked()
        if not selected_orgs:
            await callback.answer("⚠ Вы не выбрали организации для удаления.")
            return
        selected_orgs = list(map(int, selected_orgs))
        async with session_factory() as session:
            await session.execute(delete(Organization).where(Organization.id.in_(selected_orgs)))
            await session.commit()
        await callback.answer("✅ Организации удалены!")
        await dialog_manager.done()
        await dialog_manager.reset_stack()
        await dialog_manager.start(state=CommandSG.start)

    @staticmethod
    async def handle_save_selected_org_id(dialog_manager: DialogManager, item_id: str):
        dialog_manager.dialog_data["edit_org_id"] = int(item_id)
        await dialog_manager.next()

    @staticmethod
    async def handle_edit_org_field(button: Button, dialog_manager: DialogManager):
        dialog_manager.dialog_data["edit_field"] = button.widget_id
        await dialog_manager.next()

    @staticmethod
    async def handle_save_edited_field(event: Message, dialog_manager: DialogManager, text: str):
        edit_field = dialog_manager.dialog_data.get("edit_field")
        edit_org_id = dialog_manager.dialog_data.get("edit_org_id")
        if not edit_field or not edit_org_id:
            await event.answer("Ошибка: Данные для редактирования не заданы.")
            return
        session_factory = dialog_manager.middleware_data.get("session_factory")
        async with session_factory() as session:
            org = await session.get(Organization, edit_org_id)
            if org:
                setattr(org, edit_field, text)
                await session.commit()
                field_names = {
                    "address": "Адрес",
                    "phone": "Телефон",
                    "email": "Email",
                    "name": "Название организации",
                }
                await event.answer(
                    f"✅ Поле *{field_names.get(edit_field, edit_field)}* обновлено на: *{text}*",
                    parse_mode="Markdown"
                )
            else:
                await event.answer("Ошибка: Организация не найдена.")
        await dialog_manager.done()
        await dialog_manager.reset_stack()
        await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)
