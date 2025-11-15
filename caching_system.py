"""
💾 Caching System - Система кэширования
In-Memory Cache + Redis Support + LRU
"""

import time
import hashlib
import json
import pickle
from typing import Any, Optional, Callable
from functools import wraps
from collections import OrderedDict

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class LRUCache:
    """LRU (Least Recently Used) кэш"""

    def __init__(self, capacity: int = 1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            value, expires_at = self.cache[key]
            if expires_at and time.time() > expires_at:
                del self.cache[key]
                self.misses += 1
                return None
            return value
        self.misses += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, time.time() + ttl if ttl else None)

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "size": len(self.cache)
        }


class CacheManager:
    """Менеджер кэширования"""

    def __init__(self, redis_url: Optional[str] = None, max_size: int = 1000):
        self.memory_cache = LRUCache(capacity=max_size)
        self.redis_client = None

        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
            except:
                pass

    def _make_key(self, func_name: str, args, kwargs) -> str:
        key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        value = self.memory_cache.get(key)
        if value is not None:
            return value

        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    value = pickle.loads(data)
                    self.memory_cache.set(key, value)
                    return value
            except:
                pass

        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        self.memory_cache.set(key, value, ttl)

        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, pickle.dumps(value))
            except:
                pass

    def clear(self):
        self.memory_cache.clear()
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except:
                pass


_cache_manager = CacheManager()


def cached(ttl: int = 3600):
    """Декоратор для кэширования"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _cache_manager._make_key(func.__name__, args, kwargs)
            result = _cache_manager.get(key)

            if result is not None:
                return result

            result = func(*args, **kwargs)
            _cache_manager.set(key, result, ttl)
            return result

        return wrapper
    return decorator


if __name__ == "__main__":
    print("Testing cache...")

    @cached(ttl=10)
    def expensive_operation(n):
        time.sleep(1)
        return n ** 2

    start = time.time()
    result1 = expensive_operation(5)
    time1 = time.time() - start

    start = time.time()
    result2 = expensive_operation(5)
    time2 = time.time() - start

    print(f"First call: {time1:.3f}s")
    print(f"Cached call: {time2:.3f}s")
    print(f"Speedup: {time1/time2:.1f}x")
    print(f"Stats: {_cache_manager.memory_cache.get_stats()}")
