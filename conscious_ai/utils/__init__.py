"""
ConsciousAI Utils - Утилиты
Логирование, обработка ошибок, вспомогательные функции
"""

from .logger import get_logger, set_log_level, log_info, log_error, log_debug
from .exceptions import (
    # Базовые
    ConsciousAIError,
    # Память
    MemoryError,
    MemoryStorageError,
    MemoryRetrievalError,
    MemoryNotFoundError,
    MemoryConnectionError,
    # Мета-когниция
    MetaCognitiveError,
    ReflectionError,
    SelfEvaluationError,
    # Инсайты
    InsightError,
    InsightGenerationError,
    AnalogyNotFoundError,
    # Интерфейс
    InterfaceError,
    CommandParseError,
    InvalidCommandError,
    # Ядро
    CoreError,
    InitializationError,
    ConfigurationError,
    PipelineError,
    # Валидация
    ValidationError,
    InvalidInputError,
    MissingRequiredFieldError,
    # Декораторы
    handle_error,
    handle_error_async,
    safe_execute,
)

__all__ = [
    # Логирование
    'get_logger',
    'set_log_level',
    'log_info',
    'log_error',
    'log_debug',
    # Исключения
    'ConsciousAIError',
    'MemoryError',
    'MemoryStorageError',
    'MemoryRetrievalError',
    'MemoryNotFoundError',
    'MemoryConnectionError',
    'MetaCognitiveError',
    'ReflectionError',
    'SelfEvaluationError',
    'InsightError',
    'InsightGenerationError',
    'AnalogyNotFoundError',
    'InterfaceError',
    'CommandParseError',
    'InvalidCommandError',
    'CoreError',
    'InitializationError',
    'ConfigurationError',
    'PipelineError',
    'ValidationError',
    'InvalidInputError',
    'MissingRequiredFieldError',
    # Декораторы
    'handle_error',
    'handle_error_async',
    'safe_execute',
]
