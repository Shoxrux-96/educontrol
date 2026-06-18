import asyncio
import logging
import time
from typing import Dict, Tuple

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self):
        self._redis: aioredis.Redis | None = None
        self._local: Dict[str, list] = {}

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.redis_url, decode_responses=True
            )
        return self._redis

    async def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds

        try:
            r = await self._get_redis()
            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window_seconds * 2)
            _, count, _, _ = await pipe.execute()
            return count > max_requests, max_requests - count
        except Exception as e:
            logger.warning(f"Redis rate limit failed, using local fallback: {e}")
            return self._local_check(key, max_requests, window_seconds, now, window_start)

    def _local_check(
        self, key: str, max_requests: int, window_seconds: int, now: float, window_start: float
    ) -> Tuple[bool, int]:
        timestamps = self._local.get(key, [])
        timestamps = [t for t in timestamps if t > window_start]
        timestamps.append(now)
        self._local[key] = timestamps
        return len(timestamps) > max_requests, max_requests - len(timestamps)


rate_limiter = RateLimiter()
