import asyncio
import logging
from db import init_db
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from config_data.config import Config, load_config
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import command, organizations, installers, welders, other
from keyboards.main_menu import set_main_menu
from aiogram.fsm.storage.memory import MemoryStorage

# Конфигурируем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s'
)

# Инициализируем логгер
logger = logging.getLogger(__name__)

# Функция конфигурирования и запуска бота
async def start_bot():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Создаём фабрику сессий один раз
    session_factory = await init_db(config)

    # Проверяем токен
    if not config.tg_bot.token:
        raise ValueError("Bot token is not defined in the config file!")

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Настройка хранилища состояний
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Настройка диалогов
    setup_dialogs(dp)

    # Регистрируем роутеры в диспетчере
    dp.include_router(command.command_router)
    dp.include_router(organizations.org_router)
    dp.include_router(installers.installers_router)
    dp.include_router(welders.welders_router)
    dp.include_router(other.other_router)

    # Настроим главное меню бота
    await set_main_menu(bot)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Передаем session_factory в start_data диалогов
    await dp.start_polling(bot, skip_updates=True, data={"session_factory": session_factory})

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
