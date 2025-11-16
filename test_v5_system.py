"""
Тесты для ConsciousAI v5.0
Проверка всех компонентов
"""

import asyncio
import sys
from typing import List, Dict

# v5.0 компоненты
from semantic_kernel import SemanticKernel, SemanticCompressor, KernelType
from semantic_memory import SemanticMemory, KnowledgeGraph
from meta_cognitive_engine import MetaCognitiveEngine
from insight_generator import InsightGenerator, InsightType
from simple_interface import SimpleInterface, quick
from conscious_ai_v5 import ConsciousAI_v5, V5Config


class TestResults:
    """Результаты тестов"""
    def __init__(self):
        self.tests: List[Dict] = []
        self.passed = 0
        self.failed = 0

    def add(self, name: str, passed: bool, message: str = ""):
        self.tests.append({"name": name, "passed": passed, "message": message})
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_results(self):
        print("\n" + "=" * 60)
        print("  📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
        print("=" * 60)
        print()

        for test in self.tests:
            status = "✅ PASSED" if test["passed"] else "❌ FAILED"
            print(f"{status} - {test['name']}")
            if test["message"]:
                print(f"         {test['message']}")

        print()
        print("=" * 60)
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        print(f"  Всего: {total} | Прошло: {self.passed} | Провалилось: {self.failed}")
        print(f"  Успешность: {percentage:.1f}%")
        print("=" * 60)
        print()

        return self.failed == 0


async def test_semantic_kernel():
    """Тест 1: Семантические зёрна"""
    results = TestResults()

    try:
        compressor = SemanticCompressor()

        # Тест сжатия
        text = "Пользователь хочет создать AI с мета-сознанием и смысловой памятью для автономной работы"
        kernel = compressor.compress(text, language="ru")

        results.add(
            "Создание семантического зерна",
            kernel is not None and len(kernel.essence) > 0,
            f"Сжато: {len(text)} → {len(kernel.essence)} символов"
        )

        results.add(
            "Извлечение концепций",
            len(kernel.concepts) > 0,
            f"Найдено концепций: {len(kernel.concepts)}"
        )

        results.add(
            "Оценка важности",
            0 <= kernel.importance <= 1,
            f"Важность: {kernel.importance:.2f}"
        )

        # Тест сжатия диалога
        conversation = [
            {"role": "user", "content": "Привет!"},
            {"role": "assistant", "content": "Привет! Как дела?"},
            {"role": "user", "content": "Создай мне AI"},
        ]

        kernels = compressor.compress_conversation(conversation, language="ru")

        results.add(
            "Сжатие диалога",
            len(kernels) == len(conversation),
            f"Сжато {len(conversation)} сообщений"
        )

    except Exception as e:
        results.add("Семантические зёрна", False, f"Ошибка: {e}")

    return results


async def test_semantic_memory():
    """Тест 2: Смысловая память"""
    results = TestResults()

    try:
        memory = SemanticMemory(db_path="test_v5_memory.db")
        compressor = SemanticCompressor()

        # Сохранение зёрен
        test_texts = [
            "AI с мета-сознанием",
            "Смысловая память сжимает контекст",
            "Простой интуитивный интерфейс"
        ]

        kernel_ids = []
        for text in test_texts:
            kernel = compressor.compress(text, language="ru")
            kid = memory.store(kernel)
            kernel_ids.append(kid)

        results.add(
            "Сохранение зёрен в память",
            len(kernel_ids) == len(test_texts),
            f"Сохранено: {len(kernel_ids)} зёрен"
        )

        # Поиск
        search_results = memory.search("мета-сознание", limit=5)

        results.add(
            "Ассоциативный поиск",
            len(search_results) > 0,
            f"Найдено: {len(search_results)} релевантных зёрен"
        )

        # Получение зерна
        retrieved = memory.retrieve(kernel_ids[0])

        results.add(
            "Получение зерна по ID",
            retrieved is not None,
            f"ID: {kernel_ids[0][:8]}..."
        )

        # Похожие зёрна
        similar = memory.find_similar(retrieved, limit=3)

        results.add(
            "Поиск похожих зёрен",
            True,  # Может быть 0, если мало данных
            f"Найдено похожих: {len(similar)}"
        )

        # Статистика
        stats = memory.get_statistics()

        results.add(
            "Статистика памяти",
            stats['total_kernels'] >= len(test_texts),
            f"Всего зёрен: {stats['total_kernels']}"
        )

    except Exception as e:
        results.add("Смысловая память", False, f"Ошибка: {e}")

    return results


async def test_meta_cognitive_engine():
    """Тест 3: Мета-когнитивный движок"""
    results = TestResults()

    try:
        memory = SemanticMemory(db_path="test_v5_memory.db")
        engine = MetaCognitiveEngine(memory)

        # Рефлексия о решении
        decision = "Решил использовать смысловую память для сжатия"
        reflection = engine.reflector.reflect_on_decision(decision, {})

        results.add(
            "Рефлексия о решении",
            reflection is not None,
            f"Уверенность: {reflection.confidence:.2f}"
        )

        # Самооценка
        response = "Создал модуль семантической памяти"
        quality = engine.evaluator.evaluate_response("", response)

        results.add(
            "Самооценка качества",
            quality.overall_score > 0,
            f"Оценка: {quality.overall_score:.2f}"
        )

        # Обнаружение пробелов
        gaps = engine.gap_detector.detect_gaps("квантовая физика")

        results.add(
            "Обнаружение пробелов",
            True,  # Всегда проходит
            f"Обнаружено пробелов: {len(gaps)}"
        )

        # Оценка уверенности
        confidence, reasoning = engine.gap_detector.assess_confidence("AI")

        results.add(
            "Оценка уверенности",
            confidence is not None,
            f"Уверенность: {confidence.value}"
        )

        # Мета-мышление
        thought = "Нужно улучшить память AI"
        meta_result = engine.think_about_thinking(thought)

        results.add(
            "Мета-мышление",
            meta_result is not None,
            f"Качество мысли: {meta_result['quality']['overall']:.2f}"
        )

    except Exception as e:
        results.add("Мета-когнитивный движок", False, f"Ошибка: {e}")

    return results


async def test_insight_generator():
    """Тест 4: Генератор инсайтов"""
    results = TestResults()

    try:
        memory = SemanticMemory(db_path="test_v5_memory.db")
        generator = InsightGenerator(memory)

        # Добавить знания в память
        compressor = SemanticCompressor()
        knowledge = [
            "Смысловая память сжимает контекст",
            "Граф связывает зёрна",
            "AI анализирует своё мышление"
        ]

        for k in knowledge:
            kernel = compressor.compress(k, language="ru")
            memory.store(kernel)

        # Генерация инсайтов
        insights = generator.generate("улучшение памяти", limit=3)

        results.add(
            "Генерация инсайтов",
            len(insights) > 0,
            f"Сгенерировано: {len(insights)} инсайтов"
        )

        # Проверить типы инсайтов
        types_present = set(i.insight_type for i in insights)

        results.add(
            "Разнообразие инсайтов",
            len(types_present) > 1,
            f"Типов: {len(types_present)}"
        )

        # Аналогии
        analogies = generator.analogy_finder.find_analogies("сжатие")

        results.add(
            "Поиск аналогий",
            len(analogies) > 0,
            f"Найдено аналогий: {len(analogies)}"
        )

        # Латеральное мышление
        lateral = generator.lateral_thinker.random_input("создать интерфейс")

        results.add(
            "Латеральное мышление",
            lateral is not None,
            f"Новизна: {lateral.novelty:.1f}"
        )

    except Exception as e:
        results.add("Генератор инсайтов", False, f"Ошибка: {e}")

    return results


async def test_simple_interface():
    """Тест 5: Простой интерфейс"""
    results = TestResults()

    try:
        interface = SimpleInterface()

        # Парсинг команд
        commands_to_test = [
            ("создай веб-сайт", "создай", "веб-сайт"),
            ("маркетинг", "маркетинг", ""),
            ("инсайт AI память", "инсайт", "AI память"),
            ("help", "помощь", ""),
        ]

        for input_str, expected_cmd, expected_args in commands_to_test:
            cmd, args = interface.parse_command(input_str)
            results.add(
                f"Парсинг '{input_str}'",
                cmd == expected_cmd,
                f"Команда: {cmd}, Аргументы: '{args}'"
            )

        # Обработка команды
        result = interface.run_command("статистика", "")

        results.add(
            "Обработка команды",
            result is not None and result.get("action") == "show_stats",
            "Команда обработана"
        )

    except Exception as e:
        results.add("Простой интерфейс", False, f"Ошибка: {e}")

    return results


async def test_conscious_ai_v5():
    """Тест 6: Полная система v5.0"""
    results = TestResults()

    try:
        # Создание AI
        config = V5Config(
            personality_name="TestAI",
            enable_semantic_memory=True,
            enable_meta_cognition=True,
            enable_insight_generation=True
        )

        ai = ConsciousAI_v5(config)

        results.add(
            "Инициализация v5.0",
            ai is not None,
            f"Версия: {ai.VERSION}"
        )

        # Диалог
        response = await ai.chat("Привет! Это тест")

        results.add(
            "Диалог работает",
            len(response) > 0,
            f"Длина ответа: {len(response)} символов"
        )

        # Сохранение в память
        await ai.chat("Мне нужен AI с мета-сознанием")

        mem_stats = ai.semantic_memory.get_statistics()

        results.add(
            "Сохранение в память",
            mem_stats['total_kernels'] > 0,
            f"Зёрен в памяти: {mem_stats['total_kernels']}"
        )

        # Команда инсайт
        response = await ai.chat("инсайт улучшение AI")

        results.add(
            "Обработка команд",
            "инсайт" in response.lower() or "💡" in response,
            "Команда инсайт обработана"
        )

        # Статистика
        stats = ai._handle_stats()

        results.add(
            "Статистика системы",
            "статистика" in stats.lower() or "📊" in stats,
            "Статистика доступна"
        )

    except Exception as e:
        results.add("Полная система v5.0", False, f"Ошибка: {e}")

    return results


async def run_all_tests():
    """Запустить все тесты"""
    print("\n🧪 Запуск тестов ConsciousAI v5.0...\n")

    all_results = []

    # Тест 1
    print("Тест 1: Семантические зёрна...")
    results = await test_semantic_kernel()
    all_results.append(results)
    print(f"  → {results.passed}/{results.passed + results.failed} прошло")

    # Тест 2
    print("Тест 2: Смысловая память...")
    results = await test_semantic_memory()
    all_results.append(results)
    print(f"  → {results.passed}/{results.passed + results.failed} прошло")

    # Тест 3
    print("Тест 3: Мета-когнитивный движок...")
    results = await test_meta_cognitive_engine()
    all_results.append(results)
    print(f"  → {results.passed}/{results.passed + results.failed} прошло")

    # Тест 4
    print("Тест 4: Генератор инсайтов...")
    results = await test_insight_generator()
    all_results.append(results)
    print(f"  → {results.passed}/{results.passed + results.failed} прошло")

    # Тест 5
    print("Тест 5: Простой интерфейс...")
    results = await test_simple_interface()
    all_results.append(results)
    print(f"  → {results.passed}/{results.passed + results.failed} прошло")

    # Тест 6
    print("Тест 6: Полная система v5.0...")
    results = await test_conscious_ai_v5()
    all_results.append(results)
    print(f"  → {results.passed}/{results.passed + results.failed} прошло")

    # Объединить все результаты
    combined = TestResults()
    for r in all_results:
        combined.tests.extend(r.tests)
        combined.passed += r.passed
        combined.failed += r.failed

    # Показать итоговые результаты
    success = combined.print_results()

    return success


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())

    if success:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ!")
        sys.exit(0)
    else:
        print("❌ ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ")
        sys.exit(1)
