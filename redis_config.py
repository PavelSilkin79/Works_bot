from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from config import Config

redis = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)
storage = RedisStorage(redis)
