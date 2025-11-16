"""
🔄 Retry Handler - Обработчик повторных попыток с exponential backoff
Circuit Breaker Pattern + Graceful Degradation
"""

import asyncio
import time
import logging
from typing import Callable, Any, Optional, TypeVar, ParamSpec
from functools import wraps
from enum import Enum
from dataclasses import dataclass

P = ParamSpec('P')
T = TypeVar('T')


class CircuitState(Enum):
    CLOSED = "closed"  # Нормальная работа
    OPEN = "open"      # Слишком много ошибок, блокируем запросы
    HALF_OPEN = "half_open"  # Проверяем, восстановился ли сервис


@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0  # Базовая задержка в секундах
    max_delay: float = 60.0  # Максимальная задержка
    exponential_base: float = 2.0  # База для экспоненты
    jitter: bool = True  # Добавлять случайную вариацию


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


def retry_with_backoff(config: Optional[RetryConfig] = None):
    """Декоратор для retry с exponential backoff"""
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == config.max_retries:
                        logging.error(f"{func.__name__} failed after {config.max_retries} retries: {e}")
                        raise

                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random())

                    logging.warning(f"{func.__name__} failed (attempt {attempt + 1}/{config.max_retries}), retrying in {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)

            raise last_exception

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == config.max_retries:
                        raise

                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random())

                    time.sleep(delay)

            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Пример использования
if __name__ == "__main__":
    @retry_with_backoff(RetryConfig(max_retries=3, base_delay=1.0))
    async def unreliable_api_call():
        import random
        if random.random() < 0.7:
            raise Exception("API call failed")
        return "Success!"

    async def test():
        try:
            result = await unreliable_api_call()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Final error: {e}")

    asyncio.run(test())
