import redis
from app.core.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def cache_get(key: str):
    try:
        return redis_client.get(key)
    except redis.RedisError:
        return None


def cache_set(key: str, value: str, ttl: int = 60):
    try:
        redis_client.setex(key, ttl, value)
    except redis.RedisError:
        pass


def cache_delete(pattern: str):
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except redis.RedisError:
        pass
