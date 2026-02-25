import argparse
import asyncio
import logging
from redis import asyncio as aioredis
from app.core.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


async def replay_one(redis_client, message_id: str) -> bool:
    entries = await redis_client.xrange(settings.dlq_stream_key, min=message_id, max=message_id, count=1)
    if not entries:
        logger.warning(f'dlq message not found: {message_id}')
        return False

    entry_id, payload = entries[0]
    payload = dict(payload)
    payload['retry_count'] = '0'
    payload['compensated_at'] = payload.get('compensated_at') or ''
    await redis_client.xadd(settings.stream_key, payload, maxlen=100000, approximate=True)
    await redis_client.xdel(settings.dlq_stream_key, entry_id)
    logger.info(f'dlq message replayed: {entry_id} -> {settings.stream_key}')
    return True


async def replay_batch(redis_client, count: int) -> int:
    entries = await redis_client.xrange(settings.dlq_stream_key, min='-', max='+', count=count)
    replayed = 0
    for entry_id, payload in entries:
        ok = await replay_one(redis_client, entry_id)
        if ok:
            replayed += 1
    return replayed


async def _main(args):
    redis_client = await aioredis.from_url(settings.redis_url, encoding='utf-8', decode_responses=True)
    await redis_client.ping()
    try:
        if args.message_id:
            await replay_one(redis_client, args.message_id)
        else:
            total = await replay_batch(redis_client, args.count)
            logger.info(f'dlq replay done: count={total}')
    finally:
        await redis_client.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Replay messages from DLQ stream to main stream')
    parser.add_argument('--message-id', type=str, default='', help='Specific dlq stream message id to replay')
    parser.add_argument('--count', type=int, default=10, help='Replay first N messages when message-id absent')
    return parser.parse_args()


if __name__ == '__main__':
    asyncio.run(_main(parse_args()))
