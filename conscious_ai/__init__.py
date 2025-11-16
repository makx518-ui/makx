"""
ConsciousAI v5.1 - Мета-Сознательный AI
Единый пакет с профессиональной архитектурой

Рекомендация GPT-5: Создать единое пространство имён

Архитектура:
├── core/        - Ядро системы (Pipeline, AI контейнер)
├── memory/      - Смысловая память (зёрна, хранилища)
├── reasoning/   - Рассуждения (мета-когниция, инсайты)
├── interface/   - Пользовательский интерфейс
└── utils/       - Утилиты (логирование, ошибки)

Использование:
    from conscious_ai import ConsciousAI
    ai = ConsciousAI()
    response = await ai.think("Что такое сознание?")

    # Или отдельные компоненты
    from conscious_ai.memory import SemanticKernel, InMemoryStore
    from conscious_ai.utils import get_logger, ConsciousAIError
"""

__version__ = "5.1.0"
__author__ = "Claude & GPT-5 Collaboration"
__license__ = "MIT"

# Импорты из подмодулей
from .utils import (
    get_logger,
    set_log_level,
    ConsciousAIError,
    handle_error,
    safe_execute,
)

from .memory import (
    KernelType,
    SemanticKernel,
    SearchQuery,
    SearchResult,
    BaseMemoryStore,
    InMemoryStore,
)

# Ленивый импорт для тяжёлых модулей
def get_memory_store(store_type: str = "memory", **kwargs):
    """
    Получить хранилище памяти

    Args:
        store_type: "memory", "sqlite", "vector"
        **kwargs: Параметры хранилища

    Returns:
        Экземпляр BaseMemoryStore

    Пример:
        store = get_memory_store("memory")
        store = get_memory_store("sqlite", db_path="memory.db")
    """
    if store_type == "memory":
        return InMemoryStore()
    elif store_type == "sqlite":
        # TODO: Импортировать SQLiteMemoryStore когда будет готов
        from .memory.sqlite_store import SQLiteMemoryStore
        return SQLiteMemoryStore(**kwargs)
    else:
        raise ValueError(f"Unknown store type: {store_type}")


# Информация о пакете
def info():
    """Показать информацию о пакете"""
    print(f"""
╔═══════════════════════════════════════════════════════╗
║           🧠 ConsciousAI v{__version__}                      ║
║                                                       ║
║  Мета-Сознательный AI с смысловой памятью           ║
║                                                       ║
║  Модули:                                              ║
║  • memory/    - Семантические зёрна и хранилища     ║
║  • reasoning/ - Мета-когниция и инсайты             ║
║  • core/      - Ядро и Pipeline                      ║
║  • interface/ - CLI и команды                        ║
║  • utils/     - Логирование и ошибки                ║
║                                                       ║
║  Авторы: {__author__}              ║
╚═══════════════════════════════════════════════════════╝
    """)


__all__ = [
    # Версия
    '__version__',
    '__author__',
    # Утилиты
    'get_logger',
    'set_log_level',
    'ConsciousAIError',
    'handle_error',
    'safe_execute',
    # Память
    'KernelType',
    'SemanticKernel',
    'SearchQuery',
    'SearchResult',
    'BaseMemoryStore',
    'InMemoryStore',
    'get_memory_store',
    # Информация
    'info',
]
