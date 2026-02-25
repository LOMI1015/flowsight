import asyncio
import logging
from datetime import datetime, timezone
import json
from redis import asyncio as aioredis
from redis.exceptions import ResponseError
from app.core.settings import settings
from app.handlers.dataset_ingested_handler import handle_dataset_ingested

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class ProcessingWorker:
    def __init__(self) -> None:
        self._redis = None
        self._handler_map = {
            'dataset.ingested': handle_dataset_ingested,
        }

    async def connect(self) -> None:
        self._redis = await aioredis.from_url(settings.redis_url, encoding='utf-8', decode_responses=True)
        await self._redis.ping()
        logger.info(f'processing worker connected: stream={settings.stream_key}')

    async def ensure_group(self) -> None:
        try:
            await self._redis.xgroup_create(
                name=settings.stream_key,
                groupname=settings.consumer_group,
                id='0',
                mkstream=True,
            )
            logger.info(f'consumer group created: {settings.consumer_group}')
        except ResponseError as exc:
            # BUSYGROUP 表示已存在
            if 'BUSYGROUP' not in str(exc):
                raise

    async def run_once(self) -> None:
        messages = await self._redis.xreadgroup(
            groupname=settings.consumer_group,
            consumername=settings.consumer_name,
            streams={settings.stream_key: '>'},
            count=settings.batch_size,
            block=settings.block_ms,
        )
        if not messages:
            return

        for stream_name, entries in messages:
            for message_id, payload in entries:
                event_type = payload.get('event_type', '')
                handler = self._handler_map.get(event_type)
                try:
                    if handler:
                        await handler(payload)
                    else:
                        logger.warning(f'unknown event type: {event_type}')
                    await self._redis.xack(stream_name, settings.consumer_group, message_id)
                except Exception as exc:
                    await self._handle_retry(stream_name, message_id, payload, exc)

    @staticmethod
    def _calc_backoff_seconds(retry_count: int) -> int:
        # 指数退避：base * 2^(retry_count-1)，并限制最大值
        wait_seconds = settings.retry_backoff_base_seconds * (2 ** max(retry_count - 1, 0))
        return min(wait_seconds, settings.retry_backoff_max_seconds)

    async def _handle_retry(self, stream_name: str, message_id: str, payload: dict, exc: Exception) -> None:
        current_retry = int(payload.get('retry_count', '0'))
        next_retry = current_retry + 1

        if next_retry <= settings.max_retry_count:
            backoff_seconds = self._calc_backoff_seconds(next_retry)
            logger.warning(
                f'handle message failed, retrying: id={message_id}, '
                f'retry={next_retry}/{settings.max_retry_count}, backoff={backoff_seconds}s, err={exc}'
            )
            await asyncio.sleep(backoff_seconds)
            retry_payload = dict(payload)
            retry_payload['retry_count'] = str(next_retry)
            retry_payload['status'] = 'PENDING'
            retry_payload['retried_at'] = datetime.now(timezone.utc).isoformat()
            await self._redis.xadd(stream_name, retry_payload, maxlen=100000, approximate=True)
            await self._redis.xack(stream_name, settings.consumer_group, message_id)
            return

        logger.error(
            f'message exceeded max retry: id={message_id}, '
            f'retry={current_retry}, max={settings.max_retry_count}, err={exc}'
        )
        dlq_payload = dict(payload)
        dlq_payload['failed_at'] = datetime.now(timezone.utc).isoformat()
        dlq_payload['failed_reason'] = str(exc)
        dlq_payload['failed_message_id'] = message_id
        dlq_payload['failed_stream'] = stream_name
        dlq_payload['retry_count'] = str(current_retry)
        dlq_payload['dlq_metadata'] = json.dumps(
            {
                'max_retry_count': settings.max_retry_count,
                'consumer_group': settings.consumer_group,
                'consumer_name': settings.consumer_name,
            },
            ensure_ascii=False,
        )
        await self._redis.xadd(settings.dlq_stream_key, dlq_payload, maxlen=100000, approximate=True)
        logger.error(
            f'message moved to dlq: source={stream_name}, source_id={message_id}, dlq={settings.dlq_stream_key}'
        )
        await self._redis.xack(stream_name, settings.consumer_group, message_id)

    async def run_forever(self) -> None:
        await self.connect()
        await self.ensure_group()
        while True:
            await self.run_once()


async def _main() -> None:
    worker = ProcessingWorker()
    await worker.run_forever()


if __name__ == '__main__':
    asyncio.run(_main())
