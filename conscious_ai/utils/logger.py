"""
ConsciousAI - Единая система логирования
Цветной вывод + файловое логирование + уровни

Рекомендация GPT-5: Ввести единый модуль логирования
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Форматтер с цветным выводом в терминал"""

    # ANSI цвета
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
    }

    def format(self, record: logging.LogRecord) -> str:
        # Добавить цвета для терминала
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        bold = self.COLORS['BOLD']

        # Форматировать timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')

        # Короткое имя модуля
        module = record.name.split('.')[-1][:15]

        # Форматированное сообщение
        formatted = (
            f"{color}{bold}[{timestamp}]{reset} "
            f"{color}[{record.levelname:8}]{reset} "
            f"[{module:15}] "
            f"{record.getMessage()}"
        )

        # Добавить exception info если есть
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


class FileFormatter(logging.Formatter):
    """Форматтер для файлового логирования (без цветов)"""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        formatted = (
            f"[{timestamp}] "
            f"[{record.levelname:8}] "
            f"[{record.name:30}] "
            f"{record.getMessage()}"
        )

        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


class AILogger:
    """
    Единый логгер для ConsciousAI

    Использование:
        from conscious_ai.utils.logger import get_logger

        logger = get_logger(__name__)
        logger.info("Сообщение")
        logger.error("Ошибка", exc_info=True)
    """

    _instance: Optional['AILogger'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not AILogger._initialized:
            self._setup_root_logger()
            AILogger._initialized = True

    def _setup_root_logger(self):
        """Настроить корневой логгер"""
        # Получить корневой логгер для conscious_ai
        self.root_logger = logging.getLogger('conscious_ai')
        self.root_logger.setLevel(logging.DEBUG)

        # Очистить существующие handlers
        self.root_logger.handlers.clear()

        # Console handler (цветной)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.root_logger.addHandler(console_handler)

        # File handler (полный лог)
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"conscious_ai_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(FileFormatter())
        self.root_logger.addHandler(file_handler)

        # Не пропускать логи в корневой logger Python
        self.root_logger.propagate = False

    def get_logger(self, name: str) -> logging.Logger:
        """
        Получить логгер для модуля

        Args:
            name: Имя модуля (__name__)

        Returns:
            Настроенный логгер
        """
        # Убедиться что имя начинается с conscious_ai
        if not name.startswith('conscious_ai'):
            name = f'conscious_ai.{name}'

        return logging.getLogger(name)

    def set_level(self, level: str):
        """
        Установить уровень логирования

        Args:
            level: DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        log_level = level_map.get(level.upper(), logging.INFO)
        self.root_logger.setLevel(log_level)

        # Обновить console handler
        for handler in self.root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(log_level)

    def add_file_handler(self, filepath: str, level: str = 'DEBUG'):
        """
        Добавить дополнительный файловый handler

        Args:
            filepath: Путь к файлу
            level: Уровень логирования
        """
        handler = logging.FileHandler(filepath, encoding='utf-8')
        handler.setLevel(getattr(logging, level.upper(), logging.DEBUG))
        handler.setFormatter(FileFormatter())
        self.root_logger.addHandler(handler)


# Singleton instance
_logger_instance = AILogger()


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для модуля

    Args:
        name: Имя модуля (обычно __name__)

    Returns:
        Настроенный логгер

    Пример:
        logger = get_logger(__name__)
        logger.info("AI инициализирован")
        logger.debug("Детали отладки")
        logger.warning("Внимание!")
        logger.error("Ошибка!", exc_info=True)
    """
    return _logger_instance.get_logger(name)


def set_log_level(level: str):
    """
    Установить глобальный уровень логирования

    Args:
        level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    _logger_instance.set_level(level)


# Удобные функции для быстрого логирования
def log_info(message: str):
    """Быстрое INFO сообщение"""
    get_logger('quick').info(message)


def log_error(message: str, exc_info: bool = False):
    """Быстрое ERROR сообщение"""
    get_logger('quick').error(message, exc_info=exc_info)


def log_debug(message: str):
    """Быстрое DEBUG сообщение"""
    get_logger('quick').debug(message)


# Пример использования
if __name__ == "__main__":
    # Создать логгер
    logger = get_logger(__name__)

    print("🔧 Тест системы логирования:\n")

    # Различные уровни
    logger.debug("Debug сообщение (не видно в консоли по умолчанию)")
    logger.info("Info сообщение - обычная информация")
    logger.warning("Warning - предупреждение")
    logger.error("Error - ошибка")
    logger.critical("Critical - критическая ошибка")

    # С exception
    try:
        raise ValueError("Тестовое исключение")
    except Exception:
        logger.error("Поймано исключение", exc_info=True)

    # Изменить уровень
    print("\n📊 Меняю уровень на DEBUG:")
    set_log_level('DEBUG')
    logger.debug("Теперь debug виден!")

    print("\n✅ Логирование работает!")
    print("📁 Логи сохраняются в папку logs/")
