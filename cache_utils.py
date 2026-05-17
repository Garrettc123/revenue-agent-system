"""
cache_utils.py - Redis caching layer for revenue-agent-system

Provides a simple TTL-based cache backed by Redis with graceful fallback
to no-op (in-memory dict) when Redis is unavailable.
"""
import json
import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

try:
    import redis
    _redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD', None),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    _redis_client.ping()
    REDIS_AVAILABLE = True
    logging.info('[Cache] Redis connected successfully')
except Exception as e:
    _redis_client = None
    REDIS_AVAILABLE = False
    logging.warning(f'[Cache] Redis unavailable, falling back to in-memory cache: {e}')

# Fallback in-memory cache
_memory_cache: dict = {}

# Default TTLs (seconds)
TTL_STRIPE_REVENUE = int(os.getenv('CACHE_TTL_STRIPE', 120))   # 2 min
TTL_WEALTH_INDEX  = int(os.getenv('CACHE_TTL_WEALTH', 300))    # 5 min
TTL_CONDUCTOR     = int(os.getenv('CACHE_TTL_CONDUCTOR', 60))  # 1 min
TTL_HEALTH        = int(os.getenv('CACHE_TTL_HEALTH', 30))     # 30 sec


def _serialize(value: Any) -> str:
    return json.dumps(value, default=str)


def _deserialize(value: str) -> Any:
    return json.loads(value)


def cache_get(key: str) -> Optional[Any]:
    """Retrieve a cached value. Returns None on miss or error."""
    try:
        if REDIS_AVAILABLE:
            raw = _redis_client.get(key)
            if raw is not None:
                logging.debug(f'[Cache] HIT {key}')
                return _deserialize(raw)
        else:
            entry = _memory_cache.get(key)
            if entry and entry['expires'] > datetime.utcnow().timestamp():
                logging.debug(f'[Cache] MEM-HIT {key}')
                return entry['value']
    except Exception as e:
        logging.warning(f'[Cache] get error for {key}: {e}')
    logging.debug(f'[Cache] MISS {key}')
    return None


def cache_set(key: str, value: Any, ttl: int = 120) -> None:
    """Store a value in cache with TTL in seconds."""
    try:
        if REDIS_AVAILABLE:
            _redis_client.setex(key, ttl, _serialize(value))
        else:
            _memory_cache[key] = {
                'value': value,
                'expires': datetime.utcnow().timestamp() + ttl,
            }
    except Exception as e:
        logging.warning(f'[Cache] set error for {key}: {e}')


def cache_delete(key: str) -> None:
    """Invalidate a cached key."""
    try:
        if REDIS_AVAILABLE:
            _redis_client.delete(key)
        else:
            _memory_cache.pop(key, None)
    except Exception as e:
        logging.warning(f'[Cache] delete error for {key}: {e}')


def cached(key: str, ttl: int = 120):
    """
    Decorator: cache the return value of a function.

    Usage:
        @cached('revenue_data', ttl=TTL_STRIPE_REVENUE)
        def fetch_stripe_revenue():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = cache_get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_set(key, result, ttl)
            return result
        return wrapper
    return decorator


def invalidate_revenue_cache() -> None:
    """Call this after a successful Stripe webhook to flush stale data."""
    for k in ('stripe_revenue', 'wealth_index', 'masterwealth', 'conductor_dashboard'):
        cache_delete(k)
    logging.info('[Cache] Revenue cache invalidated')
