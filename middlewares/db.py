from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import async_sessionmaker

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(self, handler: Callable, event, data: Dict[str, Any]) -> Any:
        data["session_factory"] = self.session_factory
        return await handler(event, data)