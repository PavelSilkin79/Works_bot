import os
import logging
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass
from environs import Env
from typing import Optional

from pydantic import BaseModel
from redis.asyncio import Redis
import asyncpg


# === Настройка логгера ===
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "bot.log")

os.makedirs(LOGS_DIR, exist_ok=True)

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.INFO)

# 📄 Лог-файл с ротацией
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

# 🖥️ Консольный вывод
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

# Добавляем хендлеры, если ещё не добавлены
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# === Конфигурации ===

@dataclass
class DatabaseConfig:
    dbname: str
    user: str
    password: str
    host: str
    port: int


@dataclass
class TgBot:
    token: str
    chat_id: int
    owner_id: int  # добавили


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int = 0


@dataclass
class Config:
    tg_bot: TgBot
    database: DatabaseConfig
    redis: RedisConfig


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path) if path else env.read_env()

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            chat_id=env.int("CHAT_ID"),
            owner_id=env.int("BOT_OWNER_ID"),  # читаем из .env
        ),
        database=DatabaseConfig(
            dbname=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASSWORD"),
            host=env.str("DB_HOST"),
            port=env.int("DB_PORT")
        ),
        redis=RedisConfig(
            host=env.str("REDIS_HOST", "localhost"),
            port=env.int("REDIS_PORT", 6379),
            db=env.int("REDIS_DB", 0)
        )
    )


# === Проверки подключений ===

async def check_redis_connection(redis: Redis):
    try:
        await redis.ping()
        logger.info("✅ Redis подключен")
    except Exception as e:
        logger.critical(f"❌ Ошибка подключения к Redis: {e}")
        raise SystemExit("Завершение работы: Redis недоступен.")


async def check_postgres_connection(db_config: DatabaseConfig):
    try:
        conn = await asyncpg.connect(
            user=db_config.user,
            password=db_config.password,
            database=db_config.dbname,
            host=db_config.host,
            port=db_config.port
        )
        logger.info("✅ PostgreSQL подключен")
        await conn.close()
    except Exception as e:
        logger.critical(f"❌ Ошибка подключения к PostgreSQL: {e}")
        raise SystemExit("Завершение работы: PostgreSQL недоступен.")

