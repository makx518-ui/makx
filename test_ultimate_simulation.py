"""
🧪 Тестовая симуляция ConsciousAI Ultimate v4.0
Комплексный тест всех возможностей системы
"""

import asyncio
import json
from datetime import datetime
from conscious_ai_ultimate import ConsciousAI_Ultimate, UltimateConfig
from project_generator import ProjectConfig, ProjectType
import os

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_test(test_name, passed):
    status = f"{Colors.OKGREEN}✅ PASSED" if passed else f"{Colors.FAIL}❌ FAILED"
    print(f"{test_name}: {status}{Colors.ENDC}")


class TestResults:
    """Сборщик результатов тестов"""
    def __init__(self):
        self.tests = []
        self.start_time = datetime.now()

    def add_test(self, name, passed, details=""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        print_test(name, passed)

    def print_summary(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        passed = sum(1 for t in self.tests if t['passed'])
        total = len(self.tests)
        percentage = (passed / total * 100) if total > 0 else 0

        print_header("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")

        print(f"{Colors.BOLD}Всего тестов:{Colors.ENDC} {total}")
        print(f"{Colors.OKGREEN}Пройдено:{Colors.ENDC} {passed}")
        print(f"{Colors.FAIL}Провалено:{Colors.ENDC} {total - passed}")
        print(f"{Colors.BOLD}Успешность:{Colors.ENDC} {percentage:.1f}%")
        print(f"{Colors.BOLD}Время выполнения:{Colors.ENDC} {duration:.2f}s\n")

        if percentage >= 80:
            print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Система работает стабильно.{Colors.ENDC}\n")
        elif percentage >= 60:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠️  ХОРОШИЙ РЕЗУЛЬТАТ, но есть проблемы.{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}❌ ТРЕБУЕТСЯ ДОРАБОТКА!{Colors.ENDC}\n")

        # Детали проваленных тестов
        failed = [t for t in self.tests if not t['passed']]
        if failed:
            print(f"{Colors.WARNING}Проваленные тесты:{Colors.ENDC}")
            for t in failed:
                print(f"  - {t['name']}: {t['details']}")


async def test_1_multilingual_chat(ai, results):
    """Тест 1: Мультиязычный диалог"""
    print_header("ТЕСТ 1: Мультиязычный диалог")

    test_messages = [
        ("Привет! Как дела?", "ru"),
        ("Hello! How are you?", "en"),
        ("Bonjour! Comment ça va?", "fr"),
        ("¡Hola! ¿Cómo estás?", "es"),
    ]

    all_passed = True
    for msg, expected_lang in test_messages:
        print(f"\n{Colors.OKCYAN}👤 User ({expected_lang}):{Colors.ENDC} {msg}")

        try:
            response = await ai.chat(msg)
            print(f"{Colors.OKGREEN}🤖 AI:{Colors.ENDC} {response}")

            # Проверить, что ответ не пустой
            if not response or len(response) < 5:
                all_passed = False
                print_warning(f"Слишком короткий ответ")
            else:
                print_success(f"Ответ сгенерирован ({len(response)} символов)")

        except Exception as e:
            all_passed = False
            print_warning(f"Ошибка: {e}")

    results.add_test(
        "Мультиязычный диалог",
        all_passed,
        "Успешно обработаны все языки" if all_passed else "Есть ошибки в обработке"
    )

    return all_passed


async def test_2_personality_variation(ai, results):
    """Тест 2: Вариативность личности"""
    print_header("ТЕСТ 2: Вариативность ответов личности")

    test_prompt = "Расскажи про Python"
    responses = []

    print_info(f"Генерирую 3 ответа на один вопрос: '{test_prompt}'")

    for i in range(3):
        response = await ai.chat(test_prompt)
        responses.append(response)
        print(f"\n{Colors.OKCYAN}Вариант {i+1}:{Colors.ENDC}")
        print(f"  {response[:100]}...")

    # Проверить уникальность (хотя бы 50% различия)
    unique = len(set(responses)) == len(responses)

    # Проверить разную длину
    lengths = [len(r) for r in responses]
    length_variance = max(lengths) - min(lengths) > 10

    passed = unique or length_variance

    results.add_test(
        "Вариативность личности",
        passed,
        f"Генерирует разные ответы: {unique}, разная длина: {length_variance}"
    )

    return passed


async def test_3_conversation_memory(ai, results):
    """Тест 3: Память о контексте диалога"""
    print_header("ТЕСТ 3: Память о контексте диалога")

    print(f"{Colors.OKCYAN}👤 User:{Colors.ENDC} Меня зовут Алекс")
    response1 = await ai.chat("Меня зовут Алекс")
    print(f"{Colors.OKGREEN}🤖 AI:{Colors.ENDC} {response1}")

    print(f"\n{Colors.OKCYAN}👤 User:{Colors.ENDC} Я хочу создать сайт для кофейни")
    response2 = await ai.chat("Я хочу создать сайт для кофейни")
    print(f"{Colors.OKGREEN}🤖 AI:{Colors.ENDC} {response2}")

    print(f"\n{Colors.OKCYAN}👤 User:{Colors.ENDC} Как меня зовут?")
    response3 = await ai.chat("Как меня зовут?")
    print(f"{Colors.OKGREEN}🤖 AI:{Colors.ENDC} {response3}")

    # Получить сводку диалога
    summary = ai.get_conversation_summary()

    print(f"\n{Colors.OKBLUE}Сводка диалога:{Colors.ENDC}")
    print(f"  Всего сообщений: {summary.get('total_messages', 0)}")
    print(f"  Сообщений пользователя: {summary.get('user_messages', 0)}")
    print(f"  Ответов ассистента: {summary.get('assistant_messages', 0)}")

    passed = summary.get('total_messages', 0) >= 6  # 3 пары сообщений

    results.add_test(
        "Память о контексте",
        passed,
        f"Сохранено {summary.get('total_messages', 0)} сообщений"
    )

    return passed


async def test_4_autonomous_task_execution(ai, results):
    """Тест 4: Автономное выполнение задачи"""
    print_header("ТЕСТ 4: Автономное выполнение задачи")

    if not ai.agent:
        print_warning("Автономный агент не активирован")
        results.add_test("Автономное выполнение", False, "Агент не активирован")
        return False

    goal = "Создать простую структуру веб-сайта"
    print_info(f"Задача: {goal}")

    try:
        report = await ai.execute_task(goal, context={"theme": "test"})

        progress = report.get('progress', {})
        print(f"\n{Colors.OKBLUE}Результат выполнения:{Colors.ENDC}")
        print(f"  Прогресс: {progress.get('percent', 0):.1f}%")
        print(f"  Выполнено: {progress.get('completed', 0)}/{progress.get('total', 0)}")
        print(f"  Провалено: {progress.get('failed', 0)}")

        passed = progress.get('completed', 0) > 0

        results.add_test(
            "Автономное выполнение задачи",
            passed,
            f"Выполнено {progress.get('completed', 0)} из {progress.get('total', 0)} задач"
        )

        return passed

    except Exception as e:
        print_warning(f"Ошибка выполнения: {e}")
        results.add_test("Автономное выполнение задачи", False, str(e))
        return False


async def test_5_project_generation(ai, results):
    """Тест 5: Генерация проекта под ключ"""
    print_header("ТЕСТ 5: Генерация проекта под ключ")

    if not ai.project_generator:
        print_warning("Генератор проектов не активирован")
        results.add_test("Генерация проекта", False, "Генератор не активирован")
        return False

    config = ProjectConfig(
        name="test_bot_simulation",
        project_type=ProjectType.TELEGRAM_BOT,
        description="Тестовый бот для симуляции",
        features=["Команды", "Ответы"],
        include_tests=True,
        include_docs=True,
        include_docker=True,
        target_directory="./test_simulation_projects"
    )

    print_info(f"Создаю проект: {config.name}")
    print_info(f"Тип: {config.project_type.value}")

    try:
        result = await ai.create_project(config)

        if result.get('success'):
            files_created = result.get('files_created', [])
            print(f"\n{Colors.OKGREEN}Проект создан!{Colors.ENDC}")
            print(f"  Путь: {result.get('project_path')}")
            print(f"  Файлов создано: {len(files_created)}")

            print(f"\n{Colors.OKBLUE}Созданные файлы:{Colors.ENDC}")
            for f in files_created[:10]:  # Показать первые 10
                print(f"    ✓ {f}")
            if len(files_created) > 10:
                print(f"    ... и ещё {len(files_created) - 10} файлов")

            # Проверить, что основные файлы созданы
            essential_files = ['main.py', 'requirements.txt', 'README.md']
            has_essential = all(any(ef in f for f in files_created) for ef in essential_files)

            passed = len(files_created) >= 5 and has_essential

            results.add_test(
                "Генерация проекта под ключ",
                passed,
                f"Создано {len(files_created)} файлов, есть основные файлы: {has_essential}"
            )

            return passed
        else:
            print_warning(f"Ошибка: {result.get('error')}")
            results.add_test("Генерация проекта", False, result.get('error'))
            return False

    except Exception as e:
        print_warning(f"Ошибка: {e}")
        results.add_test("Генерация проекта", False, str(e))
        return False


async def test_6_tool_availability(ai, results):
    """Тест 6: Доступность инструментов"""
    print_header("ТЕСТ 6: Доступность инструментов")

    tools = ai.get_available_tools()

    print_info(f"Доступно инструментов: {len(tools)}")

    # Группировка по типам
    tool_types = {}
    for tool in tools:
        prefix = tool.split('_')[0] if '_' in tool else tool
        tool_types[prefix] = tool_types.get(prefix, 0) + 1

    print(f"\n{Colors.OKBLUE}Инструменты по категориям:{Colors.ENDC}")
    for type_name, count in sorted(tool_types.items()):
        print(f"  {type_name}: {count}")

    # Проверить основные категории
    expected_categories = ['create', 'read', 'git', 'run', 'search']
    has_categories = sum(1 for cat in expected_categories if any(cat in t for t in tools))

    passed = len(tools) >= 20 and has_categories >= 3

    results.add_test(
        "Доступность инструментов",
        passed,
        f"Доступно {len(tools)} инструментов, {has_categories}/{len(expected_categories)} категорий"
    )

    return passed


async def test_7_language_detection(ai, results):
    """Тест 7: Автоопределение языка"""
    print_header("ТЕСТ 7: Автоопределение языка")

    from conversation_manager import LanguageDetector

    detector = LanguageDetector()

    test_cases = [
        ("Привет, как дела?", "ru"),
        ("Hello, how are you?", "en"),
        ("Bonjour, comment allez-vous?", "fr"),
        ("Hola, ¿cómo estás?", "es"),
        ("Hallo, wie geht es dir?", "de"),
    ]

    correct = 0
    total = len(test_cases)

    for text, expected_lang in test_cases:
        detected = detector.detect(text)
        is_correct = detected == expected_lang

        status = "✅" if is_correct else "❌"
        print(f"{status} '{text[:30]}...' -> {detected} (ожидалось: {expected_lang})")

        if is_correct:
            correct += 1

    accuracy = (correct / total) * 100
    passed = accuracy >= 80

    results.add_test(
        "Автоопределение языка",
        passed,
        f"Точность: {accuracy:.1f}% ({correct}/{total})"
    )

    return passed


async def test_8_personality_traits(ai, results):
    """Тест 8: Черты персональности"""
    print_header("ТЕСТ 8: Черты персональности")

    profile = ai.personality.profile

    print(f"{Colors.OKBLUE}Профиль персональности:{Colors.ENDC}")
    print(f"  Имя: {profile.name}")
    print(f"  Черты: {[t.value for t in profile.traits]}")
    print(f"  Юмор: {profile.humor_level * 100:.0f}%")
    print(f"  Эмпатия: {profile.empathy_level * 100:.0f}%")
    print(f"  Формальность: {profile.formality_level * 100:.0f}%")
    print(f"  Энтузиазм: {profile.enthusiasm_level * 100:.0f}%")

    # Тест генерации приветствий
    print(f"\n{Colors.OKBLUE}Примеры приветствий:{Colors.ENDC}")
    for i in range(3):
        greeting = ai.personality.create_greeting(language='ru')
        print(f"  {i+1}. {greeting}")

    # Проверки
    has_traits = len(profile.traits) > 0
    valid_levels = all(0 <= level <= 1 for level in [
        profile.humor_level,
        profile.empathy_level,
        profile.formality_level,
        profile.enthusiasm_level
    ])

    passed = has_traits and valid_levels

    results.add_test(
        "Черты персональности",
        passed,
        f"Черт характера: {len(profile.traits)}, уровни валидны: {valid_levels}"
    )

    return passed


async def test_9_emotional_responses(ai, results):
    """Тест 9: Эмоциональные ответы"""
    print_header("ТЕСТ 9: Эмоциональные ответы")

    from personality_system import EmotionalResponseGenerator

    generator = EmotionalResponseGenerator()

    emotions = ['joy', 'sadness', 'excitement', 'concern', 'curiosity']

    print(f"{Colors.OKBLUE}Эмоциональные ответы на русском:{Colors.ENDC}")
    responses_generated = 0

    for emotion in emotions:
        response = generator.get_emotional_response(emotion, language='ru')
        if response:
            print(f"  {emotion}: {response}")
            responses_generated += 1
        else:
            print(f"  {emotion}: (нет ответа)")

    passed = responses_generated >= len(emotions) * 0.8  # Минимум 80% эмоций

    results.add_test(
        "Эмоциональные ответы",
        passed,
        f"Сгенерировано {responses_generated}/{len(emotions)} эмоций"
    )

    return passed


async def test_10_persistence(ai, results):
    """Тест 10: Персистентность (сохранение данных)"""
    print_header("ТЕСТ 10: Персистентность данных")

    print_info("Сохраняю все данные...")

    try:
        ai.save_all()

        # Проверить, что БД созданы
        db_files = [
            ai.config.conversation_db,
            # ai.config.memory_db  # Только если advanced features включены
        ]

        existing_dbs = []
        for db in db_files:
            if os.path.exists(db):
                size = os.path.getsize(db)
                existing_dbs.append(db)
                print_success(f"БД существует: {db} ({size} bytes)")
            else:
                print_warning(f"БД не найдена: {db}")

        passed = len(existing_dbs) > 0

        results.add_test(
            "Персистентность данных",
            passed,
            f"Создано БД: {len(existing_dbs)}/{len(db_files)}"
        )

        return passed

    except Exception as e:
        print_warning(f"Ошибка сохранения: {e}")
        results.add_test("Персистентность", False, str(e))
        return False


async def run_quality_assessment(results):
    """Оценка качества системы"""
    print_header("🎯 ОЦЕНКА КАЧЕСТВА СИСТЕМЫ")

    categories = {
        "Диалоговые способности": [
            "Мультиязычный диалог",
            "Вариативность личности",
            "Память о контексте",
            "Автоопределение языка",
        ],
        "Персональность и эмоции": [
            "Черты персональности",
            "Эмоциональные ответы",
        ],
        "Автономное выполнение": [
            "Автономное выполнение задачи",
            "Генерация проекта под ключ",
        ],
        "Техническая база": [
            "Доступность инструментов",
            "Персистентность данных",
        ]
    }

    print(f"{Colors.BOLD}Оценка по категориям:{Colors.ENDC}\n")

    overall_scores = []

    for category, test_names in categories.items():
        category_tests = [t for t in results.tests if t['name'] in test_names]
        if category_tests:
            passed = sum(1 for t in category_tests if t['passed'])
            total = len(category_tests)
            score = (passed / total) * 100

            overall_scores.append(score)

            emoji = "🌟" if score >= 80 else "⚠️" if score >= 60 else "❌"
            color = Colors.OKGREEN if score >= 80 else Colors.WARNING if score >= 60 else Colors.FAIL

            print(f"{emoji} {Colors.BOLD}{category}:{Colors.ENDC}")
            print(f"   {color}{score:.0f}%{Colors.ENDC} ({passed}/{total} тестов)")
            print()

    # Общая оценка
    if overall_scores:
        final_score = sum(overall_scores) / len(overall_scores)

        print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}ИТОГОВАЯ ОЦЕНКА: {Colors.ENDC}", end="")

        if final_score >= 90:
            grade = "A+"
            verdict = "ПРЕВОСХОДНО! 🏆"
            color = Colors.OKGREEN
        elif final_score >= 80:
            grade = "A"
            verdict = "ОТЛИЧНО! 🌟"
            color = Colors.OKGREEN
        elif final_score >= 70:
            grade = "B"
            verdict = "ХОРОШО ✓"
            color = Colors.OKBLUE
        elif final_score >= 60:
            grade = "C"
            verdict = "УДОВЛЕТВОРИТЕЛЬНО"
            color = Colors.WARNING
        else:
            grade = "D"
            verdict = "ТРЕБУЕТСЯ ДОРАБОТКА"
            color = Colors.FAIL

        print(f"{color}{final_score:.1f}% ({grade}) - {verdict}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

        # Рекомендации
        print(f"{Colors.BOLD}💡 Рекомендации:{Colors.ENDC}")

        if final_score >= 80:
            print("  ✅ Система работает отлично!")
            print("  ✅ Готова к использованию в production")
            print("  ✅ Все основные функции работают стабильно")
        elif final_score >= 60:
            print("  ⚠️  Система работает, но есть проблемы")
            print("  ⚠️  Рекомендуется доработка проваленных тестов")
        else:
            print("  ❌ Требуется серьёзная доработка")
            print("  ❌ Много критических ошибок")


async def main():
    """Главная функция тестирования"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║      🧪 ТЕСТОВАЯ СИМУЛЯЦИЯ ConsciousAI Ultimate v4.0 🧪           ║")
    print("║                Комплексное тестирование системы                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    # Создать конфигурацию для тестов
    config = UltimateConfig(
        personality_name="TestAI",
        personality_traits=["friendly", "creative", "enthusiastic"],
        humor_level=0.7,
        empathy_level=0.9,
        formality_level=0.2,
        use_llm=False,  # Без LLM для тестов
        enable_autonomous_agent=True,
        enable_project_generation=True,
        enable_advanced_features=False,  # Отключить advanced для простоты
        conversation_db="test_simulation_conversations.db",
    )

    print_info("Инициализация системы...")
    ai = ConsciousAI_Ultimate(config)

    # Результаты
    results = TestResults()

    # Запуск всех тестов
    await test_1_multilingual_chat(ai, results)
    await test_2_personality_variation(ai, results)
    await test_3_conversation_memory(ai, results)
    await test_4_autonomous_task_execution(ai, results)
    await test_5_project_generation(ai, results)
    await test_6_tool_availability(ai, results)
    await test_7_language_detection(ai, results)
    await test_8_personality_traits(ai, results)
    await test_9_emotional_responses(ai, results)
    await test_10_persistence(ai, results)

    # Итоговая сводка
    results.print_summary()

    # Оценка качества
    await run_quality_assessment(results)

    # Сохранить отчёт
    report_path = "test_simulation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "tests": results.tests,
            "summary": {
                "total": len(results.tests),
                "passed": sum(1 for t in results.tests if t['passed']),
                "failed": sum(1 for t in results.tests if not t['passed']),
                "duration_seconds": (datetime.now() - results.start_time).total_seconds()
            }
        }, f, ensure_ascii=False, indent=2)

    print(f"\n{Colors.OKBLUE}📄 Отчёт сохранён в: {report_path}{Colors.ENDC}")

    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                    ✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ✅                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")


if __name__ == "__main__":
    asyncio.run(main())
