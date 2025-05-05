from functools import wraps
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config_data.config import load_config
from db import models  # Убедись, что путь правильный



config = load_config()
OWNER_ID = config.tg_bot.owner_id


# Получение user_id из события
def get_user_id(event):
    if isinstance(event, Message) or isinstance(event, CallbackQuery):
        return event.from_user.id
    return None


# Универсальный ответ
async def answer_event(event, text: str):
    if isinstance(event, CallbackQuery):
        await event.answer(text, show_alert=True)
    elif isinstance(event, Message):
        await event.answer(text)


# 👑 Только для владельца
def owner_only(handler):
    @wraps(handler)
    async def wrapper(event, *args, **kwargs):
        user_id = get_user_id(event)
        if user_id != OWNER_ID:
            await answer_event(event, "❌ Только владелец может использовать эту команду.")
            return
        return await handler(event, *args, **kwargs)
    return wrapper


# ✅ Для владельца и админов
def admin_required(handler):
    @wraps(handler)
    async def wrapper(event, *args, **kwargs):
        user_id = get_user_id(event)

        # Если владелец — пускаем сразу
        if user_id == OWNER_ID:
            return await handler(event, *args, **kwargs)

        # Достаём session из kwargs или DialogManager
        session: AsyncSession = kwargs.get("session")
        dialog_manager: DialogManager = kwargs.get("dialog_manager")

        if not session and dialog_manager:
            session = dialog_manager.middleware_data.get("session")

        if not session:
            await answer_event(event, "⚠️ Внутренняя ошибка: не передана сессия БД.")
            return

        # Проверка в БД
        result = await session.execute(select(Admin).where(Admin.user_id == user_id))
        admin = result.scalar_one_or_none()

        if admin is None:
            await answer_event(event, "❌ У вас нет доступа.")
            return

        return await handler(event, *args, **kwargs)

    return wrapper
