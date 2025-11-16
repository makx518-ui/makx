"""
ConsciousAI - Иерархия исключений
Стандартизированная обработка ошибок

Рекомендация GPT-5: Создать BaseError и наследники для модулей
"""

from typing import Optional, Dict, Any


class ConsciousAIError(Exception):
    """
    Базовое исключение для всех ошибок ConsciousAI

    Все ошибки системы наследуются от этого класса,
    что позволяет ловить все ошибки одним except
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        base = f"[{self.error_code}] {self.message}"
        if self.details:
            base += f" | Details: {self.details}"
        return base

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация ошибки"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


# ============================================
# ОШИБКИ ПАМЯТИ (Memory)
# ============================================

class MemoryError(ConsciousAIError):
    """Базовая ошибка модуля памяти"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "MEMORY_ERROR", details)


class MemoryStorageError(MemoryError):
    """Ошибка сохранения в память"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, details)
        self.error_code = "MEMORY_STORAGE_ERROR"


class MemoryRetrievalError(MemoryError):
    """Ошибка получения из памяти"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, details)
        self.error_code = "MEMORY_RETRIEVAL_ERROR"


class MemoryNotFoundError(MemoryError):
    """Запись не найдена в памяти"""

    def __init__(self, kernel_id: str):
        super().__init__(
            f"Kernel not found: {kernel_id}",
            {"kernel_id": kernel_id}
        )
        self.error_code = "MEMORY_NOT_FOUND"


class MemoryConnectionError(MemoryError):
    """Ошибка подключения к хранилищу"""

    def __init__(self, storage_type: str, details: Optional[Dict] = None):
        super().__init__(
            f"Cannot connect to {storage_type} storage",
            details
        )
        self.error_code = "MEMORY_CONNECTION_ERROR"


# ============================================
# ОШИБКИ МЕТА-КОГНИЦИИ (Meta-Cognitive)
# ============================================

class MetaCognitiveError(ConsciousAIError):
    """Базовая ошибка мета-когнитивного модуля"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "META_COGNITIVE_ERROR", details)


class ReflectionError(MetaCognitiveError):
    """Ошибка при рефлексии"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, details)
        self.error_code = "REFLECTION_ERROR"


class SelfEvaluationError(MetaCognitiveError):
    """Ошибка при самооценке"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, details)
        self.error_code = "SELF_EVALUATION_ERROR"


# ============================================
# ОШИБКИ ИНСАЙТОВ (Insights)
# ============================================

class InsightError(ConsciousAIError):
    """Базовая ошибка генерации инсайтов"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "INSIGHT_ERROR", details)


class InsightGenerationError(InsightError):
    """Не удалось сгенерировать инсайт"""

    def __init__(self, topic: str, reason: str):
        super().__init__(
            f"Cannot generate insight for '{topic}': {reason}",
            {"topic": topic, "reason": reason}
        )
        self.error_code = "INSIGHT_GENERATION_ERROR"


class AnalogyNotFoundError(InsightError):
    """Аналогия не найдена"""

    def __init__(self, concept: str):
        super().__init__(
            f"No analogy found for concept: {concept}",
            {"concept": concept}
        )
        self.error_code = "ANALOGY_NOT_FOUND"


# ============================================
# ОШИБКИ ИНТЕРФЕЙСА (Interface)
# ============================================

class InterfaceError(ConsciousAIError):
    """Базовая ошибка интерфейса"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "INTERFACE_ERROR", details)


class CommandParseError(InterfaceError):
    """Ошибка парсинга команды"""

    def __init__(self, command: str, reason: str):
        super().__init__(
            f"Cannot parse command '{command}': {reason}",
            {"command": command, "reason": reason}
        )
        self.error_code = "COMMAND_PARSE_ERROR"


class InvalidCommandError(InterfaceError):
    """Неизвестная команда"""

    def __init__(self, command: str):
        super().__init__(
            f"Unknown command: {command}",
            {"command": command}
        )
        self.error_code = "INVALID_COMMAND"


# ============================================
# ОШИБКИ ЯДРА (Core)
# ============================================

class CoreError(ConsciousAIError):
    """Базовая ошибка ядра AI"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "CORE_ERROR", details)


class InitializationError(CoreError):
    """Ошибка инициализации системы"""

    def __init__(self, component: str, reason: str):
        super().__init__(
            f"Cannot initialize {component}: {reason}",
            {"component": component, "reason": reason}
        )
        self.error_code = "INITIALIZATION_ERROR"


class ConfigurationError(CoreError):
    """Ошибка конфигурации"""

    def __init__(self, param: str, value: Any, expected: str):
        super().__init__(
            f"Invalid configuration: {param}={value}, expected {expected}",
            {"param": param, "value": value, "expected": expected}
        )
        self.error_code = "CONFIGURATION_ERROR"


class PipelineError(CoreError):
    """Ошибка в pipeline обработки"""

    def __init__(self, stage: str, reason: str):
        super().__init__(
            f"Pipeline failed at stage '{stage}': {reason}",
            {"stage": stage, "reason": reason}
        )
        self.error_code = "PIPELINE_ERROR"


# ============================================
# ОШИБКИ ВАЛИДАЦИИ (Validation)
# ============================================

class ValidationError(ConsciousAIError):
    """Базовая ошибка валидации"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class InvalidInputError(ValidationError):
    """Невалидные входные данные"""

    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            f"Invalid input for '{field}': {reason}",
            {"field": field, "value": str(value)[:100], "reason": reason}
        )
        self.error_code = "INVALID_INPUT"


class MissingRequiredFieldError(ValidationError):
    """Отсутствует обязательное поле"""

    def __init__(self, field: str):
        super().__init__(
            f"Missing required field: {field}",
            {"field": field}
        )
        self.error_code = "MISSING_REQUIRED_FIELD"


# ============================================
# УТИЛИТЫ ДЛЯ ОБРАБОТКИ ОШИБОК
# ============================================

def handle_error(func):
    """
    Декоратор для автоматической обработки ошибок

    Использование:
        @handle_error
        def risky_function():
            ...
    """
    from functools import wraps
    from .logger import get_logger

    logger = get_logger(func.__module__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConsciousAIError as e:
            logger.error(f"ConsciousAI Error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise CoreError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                details={"original_error": type(e).__name__}
            ) from e

    return wrapper


def handle_error_async(func):
    """Асинхронная версия декоратора обработки ошибок"""
    from functools import wraps
    from .logger import get_logger

    logger = get_logger(func.__module__)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConsciousAIError as e:
            logger.error(f"ConsciousAI Error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise CoreError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                details={"original_error": type(e).__name__}
            ) from e

    return wrapper


def safe_execute(func, *args, default=None, **kwargs):
    """
    Безопасное выполнение функции с fallback

    Args:
        func: Функция для выполнения
        *args: Аргументы
        default: Значение по умолчанию при ошибке
        **kwargs: Именованные аргументы

    Returns:
        Результат функции или default
    """
    from .logger import get_logger
    logger = get_logger('safe_execute')

    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Safe execute caught error: {e}")
        return default


# Пример использования
if __name__ == "__main__":
    print("🔧 Тест системы исключений:\n")

    # Тест базового исключения
    try:
        raise ConsciousAIError("Тестовая ошибка", "TEST_001", {"key": "value"})
    except ConsciousAIError as e:
        print(f"✅ Базовое исключение: {e}")
        print(f"   Dict: {e.to_dict()}\n")

    # Тест ошибки памяти
    try:
        raise MemoryNotFoundError("kernel-123")
    except MemoryError as e:
        print(f"✅ Ошибка памяти: {e}\n")

    # Тест ошибки инсайта
    try:
        raise InsightGenerationError("AI память", "недостаточно данных")
    except InsightError as e:
        print(f"✅ Ошибка инсайта: {e}\n")

    # Тест декоратора
    @handle_error
    def failing_function():
        raise ValueError("Внутренняя ошибка")

    try:
        failing_function()
    except CoreError as e:
        print(f"✅ Декоратор поймал: {e}\n")

    # Тест safe_execute
    def divide(a, b):
        return a / b

    result = safe_execute(divide, 10, 0, default=-1)
    print(f"✅ Safe execute: 10/0 = {result} (fallback)\n")

    print("✅ Система исключений работает!")
