"""Cache utility with Redis backend and automatic in-memory fallback."""

import asyncio
import fnmatch
import json
import time
from datetime import datetime
from typing import Any, Optional

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class _DatetimeEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def _serialize(value: Any) -> str:
    return json.dumps(value, cls=_DatetimeEncoder)


def _deserialize(raw: str) -> Any:
    return json.loads(raw)


class _MemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at != -1 and time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        expires_at = time.monotonic() + ttl if ttl > 0 else -1
        async with self._lock:
            self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def keys(self) -> list[str]:
        now = time.monotonic()
        async with self._lock:
            valid = [
                k for k, (_, exp) in self._store.items()
                if exp == -1 or now <= exp
            ]
        return valid

    def size(self) -> int:
        return len(self._store)


class CacheManager:
    def __init__(self) -> None:
        self._redis: Any = None
        self._memory = _MemoryCache()
        self._redis_ok = False

        if settings.REDIS_ENABLED:
            self._try_connect_redis()

    def _try_connect_redis(self) -> None:
        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            logger.info("Redis client created | url={}", settings.REDIS_URL)
        except Exception as exc:
            logger.warning("Redis client creation failed: {} — using in-memory cache", exc)
            self._redis = None

    async def _ping_redis(self) -> bool:
        if self._redis is None:
            return False
        try:
            await self._redis.ping()
            return True
        except Exception as exc:
            logger.warning("Redis ping failed: {} — switching to in-memory cache", exc)
            self._redis_ok = False
            return False

    async def _ensure_redis(self) -> bool:
        if not settings.REDIS_ENABLED or self._redis is None:
            return False
        if not self._redis_ok:
            self._redis_ok = await self._ping_redis()
        return self._redis_ok

    async def get(self, key: str) -> Optional[Any]:
        try:
            if await self._ensure_redis():
                raw: Optional[str] = await self._redis.get(key)
            else:
                raw = await self._memory.get(key)

            if raw is None:
                return None
            return _deserialize(raw)
        except Exception as exc:
            logger.error("Cache get error for key '{}': {}", key, exc)
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        try:
            serialised = _serialize(value)
            if await self._ensure_redis():
                if ttl > 0:
                    await self._redis.setex(key, ttl, serialised)
                else:
                    await self._redis.set(key, serialised)
            else:
                await self._memory.set(key, serialised, ttl=ttl)
        except Exception as exc:
            logger.error("Cache set error for key '{}': {}", key, exc)

    async def delete(self, key: str) -> None:
        try:
            if await self._ensure_redis():
                await self._redis.delete(key)
            else:
                await self._memory.delete(key)
        except Exception as exc:
            logger.error("Cache delete error for key '{}': {}", key, exc)

    async def clear_pattern(self, pattern: str) -> None:
        try:
            if await self._ensure_redis():
                cursor = 0
                deleted = 0
                while True:
                    cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self._redis.delete(*keys)
                        deleted += len(keys)
                    if cursor == 0:
                        break
                logger.debug("Cleared {} Redis keys matching '{}'", deleted, pattern)
            else:
                all_keys = await self._memory.keys()
                matched = [k for k in all_keys if fnmatch.fnmatch(k, pattern)]
                for k in matched:
                    await self._memory.delete(k)
                logger.debug("Cleared {} in-memory keys matching '{}'", len(matched), pattern)
        except Exception as exc:
            logger.error("Cache clear_pattern error for pattern '{}': {}", pattern, exc)

    def is_redis_connected(self) -> bool:
        return self._redis_ok and self._redis is not None

    async def health_check(self) -> dict:
        redis_connected = await self._ping_redis() if self._redis is not None else False
        return {
            "backend": "redis" if redis_connected else "memory",
            "redis_enabled": settings.REDIS_ENABLED,
            "redis_connected": redis_connected,
            "memory_keys": self._memory.size(),
            "status": "ok",
        }


cache = CacheManager()
