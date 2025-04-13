import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from db import Base  # импортируем все модели
from config_data.config import load_config  # путь к конфигу

# Настройка логирования из файла alembic.ini
config = context.config
fileConfig(config.config_file_name)

# Загружаем конфиг из Python (а не из alembic.ini)
app_config = load_config()

# Подключаем мета-данные из моделей
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций в оффлайн-режиме."""
    # Формируем строку подключения программно
    url = f"postgresql+asyncpg://{app_config.database.user}:{app_config.database.password}@{app_config.database.host}/{app_config.database.dbname}"
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запуск миграций в онлайн-режиме."""
    # Формируем строку подключения программно
    url = f"postgresql+asyncpg://{app_config.database.user}:{app_config.database.password}@{app_config.database.host}/{app_config.database.dbname}"
    engine = create_async_engine(url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)

    await engine.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
