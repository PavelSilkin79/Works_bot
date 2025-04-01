from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config_data.config import Config, load_config

# Создаем базовый класс для моделей
Base = declarative_base()

# Асинхронная функция создания подключения к базе данных
async def init_db(config: Config):
    url = f"postgresql+asyncpg://{config.database.user}:{config.database.password}@{config.database.host}/{config.database.dbname}"
    engine = create_async_engine(url, echo=True)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    # Создаем все таблицы, если их еще нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return session_factory

# Асинхронный контекст-менеджер для получения сессии
async def get_db(session_factory):
    async with session_factory() as session:
        yield session