from typing import Any, Dict
from redis import asyncio as aioredis
from redis.asyncio import Redis
import logging
from app.core.settings import settings

logger = logging.getLogger(__name__)


class RedisStreamPublisher:
    _redis: Redis | None = None

    @classmethod
    async def connect(cls) -> None:
        if cls._redis is not None:
            return
        cls._redis = await aioredis.from_url(settings.redis_url, encoding='utf-8', decode_responses=True)
        await cls._redis.ping()

    @classmethod
    async def close(cls) -> None:
        if cls._redis is None:
            return
        await cls._redis.close()
        cls._redis = None

    @classmethod
    async def publish_dataset_ingested(cls, event_data: Dict[str, Any]) -> None:
        if cls._redis is None:
            await cls.connect()

        payload = {key: str(value) for key, value in event_data.items()}
        await cls._redis.xadd(settings.dataset_ingested_stream_key, payload, maxlen=100000, approximate=True)
        logger.info(
            f"stream published: key={settings.dataset_ingested_stream_key}, "
            f"event=dataset.ingested, dataset_id={payload.get('dataset_id')}"
        )
