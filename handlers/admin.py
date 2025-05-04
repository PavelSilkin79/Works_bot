from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import insert, update, delete
from db import models

admin_router = Router()

@admin_router.message(F.text.startswith("/add_admin"))
async def add_admin(message: Message, session_factory):
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("❌ Используй: /add_admin <tg_id>")

    tg_id = int(parts[1])
    async with session_factory() as session:
        await session.merge(User(tg_id=tg_id, is_admin=True))
        await session.commit()
    await message.answer(f"✅ Пользователь {tg_id} теперь админ.")

@admin_router.message(F.text.startswith("/remove_admin"))
async def remove_admin(message: Message, session_factory):
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("❌ Используй: /remove_admin <tg_id>")

    tg_id = int(parts[1])
    async with session_factory() as session:
        stmt = update(User).where(User.tg_id == tg_id).values(is_admin=False)
        await session.execute(stmt)
        await session.commit()
    await message.answer(f"✅ Пользователь {tg_id} больше не админ.")
