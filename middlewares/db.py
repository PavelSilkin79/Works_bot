from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from models import User

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(self, handler: Callable, event, data: Dict[str, Any]) -> Any:
        data["session_factory"] = self.session_factory
        return await handler(event, data)


class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            async with self.session_factory() as session:
                stmt = select(User).where(User.tg_id == event.from_user.id)
                result = await session.execute(stmt)
                user: User = result.scalar()

                data["is_admin"] = user.is_admin if user else False
                data["user_exists"] = user is not None

        return await handler(event, data)