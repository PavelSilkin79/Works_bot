import asyncio
import logging
from db import init_db
from aiogram import Bot, Dispatcher
from aiogram_dialog import Dialog, setup_dialogs#, DialogRegistry
from config_data.config import Config, load_config
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import command, organizations, other
from keyboards.main_menu import set_main_menu
from aiogram.fsm.storage.memory import MemoryStorage




    # Конфигурируем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s')
#logger.error("Starting bot")

    # Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def start_bot():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Проверяем токен
    if not config.tg_bot.token:
        raise ValueError("Bot token is not defined in the config file!")

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    setup_dialogs(dp)

 # Регистрируем роутеры в диспетчере
    dp.include_routers(command.command_router)
    dp.include_routers(organizations.org_router)
    dp.include_routers(other.other_router)



    # Настраиваем главное меню бота
    await set_main_menu(bot)


    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await init_db()

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
