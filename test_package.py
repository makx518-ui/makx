#!/usr/bin/env python3
"""
Тест пакета conscious_ai
Проверка всех компонентов новой архитектуры
"""

import sys
import os

# Добавить текущую директорию в path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Тест 1: Импорты работают"""
    print("🔍 Тест 1: Импорты...")

    try:
        # Главный пакет
        import conscious_ai
        assert conscious_ai.__version__ == "5.1.0"

        # Утилиты
        from conscious_ai.utils import get_logger, ConsciousAIError, handle_error

        # Память
        from conscious_ai.memory import (
            KernelType,
            SemanticKernel,
            SearchQuery,
            BaseMemoryStore,
            InMemoryStore,
            SQLiteMemoryStore
        )

        print("  ✅ Все импорты работают")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def test_logger():
    """Тест 2: Логирование"""
    print("🔍 Тест 2: Логирование...")

    try:
        from conscious_ai.utils import get_logger, set_log_level

        logger = get_logger("test_module")

        # Проверить что логгер создан
        assert logger is not None
        assert "conscious_ai" in logger.name

        # Логировать (не должно падать)
        logger.info("Тестовое сообщение")
        logger.warning("Предупреждение")

        print("  ✅ Логирование работает")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def test_exceptions():
    """Тест 3: Система исключений"""
    print("🔍 Тест 3: Исключения...")

    try:
        from conscious_ai.utils import (
            ConsciousAIError,
            MemoryError,
            MemoryNotFoundError,
            CoreError
        )

        # Создать исключение
        error = ConsciousAIError("Test", "CODE_001", {"key": "value"})
        assert error.error_code == "CODE_001"
        assert "key" in error.details

        # Проверить наследование
        mem_error = MemoryNotFoundError("kernel-123")
        assert isinstance(mem_error, MemoryError)
        assert isinstance(mem_error, ConsciousAIError)

        # Проверить сериализацию
        error_dict = error.to_dict()
        assert "error" in error_dict
        assert "message" in error_dict

        print("  ✅ Система исключений работает")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def test_semantic_kernel():
    """Тест 4: Семантические зёрна"""
    print("🔍 Тест 4: SemanticKernel...")

    try:
        from conscious_ai.memory import SemanticKernel, KernelType

        # Создать зерно
        kernel = SemanticKernel(
            essence="Тестовое зерно",
            concepts=["тест", "зерно"],
            kernel_type=KernelType.FACT,
            importance=0.8,
            priority=5,
            tags=["test"]
        )

        # Проверить поля
        assert kernel.essence == "Тестовое зерно"
        assert len(kernel.concepts) == 2
        assert kernel.importance == 0.8
        assert kernel.priority == 5

        # Активация
        old_count = kernel.activation_count
        kernel.activate()
        assert kernel.activation_count == old_count + 1
        assert kernel.last_accessed is not None

        # Сериализация
        data = kernel.to_dict()
        assert data["essence"] == "Тестовое зерно"
        assert data["kernel_type"] == "fact"

        # Десериализация
        restored = SemanticKernel.from_dict(data)
        assert restored.essence == kernel.essence

        print("  ✅ SemanticKernel работает")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_in_memory_store():
    """Тест 5: In-Memory хранилище"""
    print("🔍 Тест 5: InMemoryStore...")

    try:
        from conscious_ai.memory import (
            InMemoryStore,
            SemanticKernel,
            KernelType,
            SearchQuery
        )

        store = InMemoryStore()

        # Сохранить
        kernel1 = SemanticKernel(
            essence="AI с мета-сознанием",
            concepts=["ai", "мета", "сознание"],
            kernel_type=KernelType.GOAL,
            importance=0.9
        )
        kernel2 = SemanticKernel(
            essence="Память сжимает контекст",
            concepts=["память", "сжатие"],
            kernel_type=KernelType.FACT,
            importance=0.7
        )

        id1 = store.save(kernel1)
        id2 = store.save(kernel2)

        # Получить
        retrieved = store.get(id1)
        assert retrieved.essence == "AI с мета-сознанием"

        # Поиск
        query = SearchQuery(text="мета-сознание", limit=5)
        results = store.search(query)
        assert len(results) > 0

        # Статистика
        stats = store.stats()
        assert stats["total_kernels"] == 2

        # Связать
        store.connect(id1, id2)
        connected = store.get_connected(id1)
        assert len(connected) == 1

        # Удалить
        store.delete(id2)
        stats = store.stats()
        assert stats["total_kernels"] == 1

        print("  ✅ InMemoryStore работает")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sqlite_store():
    """Тест 6: SQLite хранилище"""
    print("🔍 Тест 6: SQLiteMemoryStore...")

    try:
        from conscious_ai.memory import (
            SQLiteMemoryStore,
            SemanticKernel,
            KernelType,
            SearchQuery
        )

        # Создать хранилище (тестовая БД)
        store = SQLiteMemoryStore(db_path="test_package_sqlite.db")

        # Сохранить
        kernel = SemanticKernel(
            essence="SQLite тест",
            concepts=["sqlite", "тест"],
            kernel_type=KernelType.FACT,
            importance=0.8,
            tags=["test"]
        )

        kid = store.save(kernel)

        # Получить
        retrieved = store.get(kid)
        assert retrieved.essence == "SQLite тест"

        # Поиск
        query = SearchQuery(min_importance=0.5, limit=10)
        results = store.search(query)
        assert len(results) > 0

        # Статистика
        stats = store.stats()
        assert stats["total_kernels"] >= 1
        assert stats["storage_size_bytes"] > 0

        # Очистка
        store.delete(kid)

        print("  ✅ SQLiteMemoryStore работает")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_handle_error_decorator():
    """Тест 7: Декоратор обработки ошибок"""
    print("🔍 Тест 7: @handle_error...")

    try:
        from conscious_ai.utils import handle_error, CoreError

        @handle_error
        def failing_function():
            raise ValueError("Внутренняя ошибка")

        # Декоратор должен преобразовать в CoreError
        try:
            failing_function()
            assert False, "Должно было быть исключение"
        except CoreError as e:
            assert "Unexpected error" in str(e)

        print("  ✅ @handle_error работает")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def test_package_info():
    """Тест 8: Информация о пакете"""
    print("🔍 Тест 8: Package info...")

    try:
        import conscious_ai

        assert conscious_ai.__version__ == "5.1.0"
        assert "Claude" in conscious_ai.__author__

        # info() не должен падать
        # conscious_ai.info()  # Закомментировано, чтобы не загромождать вывод

        print("  ✅ Package info корректен")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def main():
    """Запустить все тесты"""
    print("\n" + "=" * 60)
    print("  🧪 ТЕСТИРОВАНИЕ ПАКЕТА conscious_ai v5.1")
    print("=" * 60 + "\n")

    tests = [
        test_imports,
        test_logger,
        test_exceptions,
        test_semantic_kernel,
        test_in_memory_store,
        test_sqlite_store,
        test_handle_error_decorator,
        test_package_info,
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1

    # Итоги
    print("\n" + "=" * 60)
    print("  📊 ИТОГИ")
    print("=" * 60)

    total = passed + failed
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\n  Всего тестов: {total}")
    print(f"  Прошло: {passed} ✅")
    print(f"  Провалилось: {failed} ❌")
    print(f"  Успешность: {percentage:.1f}%\n")

    if failed == 0:
        print("  🎉 ВСЕ ТЕСТЫ ПРОШЛИ!")
    else:
        print("  ⚠️  ЕСТЬ ПРОБЛЕМЫ")

    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
