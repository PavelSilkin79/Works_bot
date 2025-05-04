from aiogram_dialog import DialogManager

async def safe_send(dialog_manager: DialogManager, text: str):
    event = dialog_manager.event

    if hasattr(event, "message") and event.message:
        await event.message.answer(text)
    elif hasattr(event, "callback_query") and event.callback_query.message:
        await event.callback_query.message.answer(text)
    else:
        raise RuntimeError("Не удалось отправить сообщение: неизвестный тип события")