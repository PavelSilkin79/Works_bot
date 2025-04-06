from aiogram import Router
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON

other_router = Router()


# Этот хэндлер будет реагировать на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@other_router.message()
async def send_echo(message: Message):
    await message.answer(text=LEXICON['other_answer'])