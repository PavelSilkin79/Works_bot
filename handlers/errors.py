from aiogram import Router, F
from aiogram.types import ErrorEvent
from aiogram_dialog.api.exceptions import UnknownIntent
from aiogram_dialog import DialogManager, StartMode
from aiogram.utils.markdown import hbold

from states import CommandSG  # Или твое стартовое состояние

error_router = Router(name="errors")


@error_router.errors()
async def unknown_intent_handler(event: ErrorEvent, dialog_manager: DialogManager):
    err = event.exception

    if isinstance(err, UnknownIntent):
        if event.update.message:
            await event.update.message.answer(
                "⚠️ Что-то пошло не так. Давай начнём сначала."
            )
        elif event.update.callback_query:
            await event.update.callback_query.message.answer(
                "⚠️ Диалог не найден или устарел. Давай начнём сначала."
            )

        await dialog_manager.start(CommandSG.start, mode=StartMode.RESET_STACK)
        return

    # логируем другие ошибки
    import logging
    logging.exception("Unhandled error", exc_info=err)
