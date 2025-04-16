import asyncio
import logging
from db import init_db
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from config_data.config import Config, load_config, check_redis_connection, check_postgres_connection
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import command, organizations, installers, welders, other
from keyboards.main_menu import set_main_menu
from middlewares.db import DBSessionMiddleware  # путь к мидлваре
#from aiogram.fsm.storage.memory import MemoryStorage
from redis.asyncio import Redis

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

    # Настройка Redis-клиента
    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        decode_responses=True
    )

        # Проверки подключений
    await check_redis_connection(redis)
    await check_postgres_connection(config.database)

    logger.info("✅ Все подключения установлены. Запускаем бота...")

    # FSM Redis Storage
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))

    # Проверяем токен
    if not config.tg_bot.token:
        raise ValueError("Bot token is not defined in the config file!")

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Настройка хранилища состояний
#    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

        # Инициализируем сессию
    session_factory: async_sessionmaker = await init_db(config)

    # Подключаем middleware
    dp.message.middleware(DBSessionMiddleware(session_factory))
    dp.callback_query.middleware(DBSessionMiddleware(session_factory))

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
        logger.warning("⛔️ Бот остановлен.")
