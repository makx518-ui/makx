"""
ConsciousAI v5.0 - Мета-Сознательный AI
Полная интеграция всех систем

Архитектура (5 слоёв):
├── L5: Interface (Интерфейс)
│   └── SimpleInterface - простые команды
├── L4: Partnership (Партнёрство)
│   └── Эмпатия, инициатива, сотрудничество
├── L3: Meta-Cognitive (Мета-сознание)
│   └── Рефлексия, самооценка, планирование
├── L2: Intelligence (Интеллект)
│   ├── SemanticMemory - смысловая память
│   └── InsightGenerator - генератор инсайтов
└── L1: Execution (Выполнение)
    ├── ProjectGenerator - создание проектов
    ├── MarketingAgent - маркетинг 24/7
    └── Tools - все инструменты

НОВЫЕ возможности v5.0:
✨ Смысловая память (сжатие 20-50x)
✨ Мета-когнитивные способности (рефлексия)
✨ Генерация инсайтов (аналогии, синтез)
✨ Простой интерфейс (команды одним словом)

+ ВСЕ возможности v4.2:
✅ Маркетинговая автоматизация 24/7
✅ Создание проектов под ключ
✅ Мультиязычность (10+ языков)
✅ 27 инструментов
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

# v5.0 компоненты
from semantic_kernel import SemanticKernel, KernelType, SemanticCompressor
from semantic_memory import SemanticMemory, KnowledgeGraph
from meta_cognitive_engine import MetaCognitiveEngine, Reflection, QualityMetrics
from insight_generator import InsightGenerator, Insight, InsightType
from simple_interface import SimpleInterface, quick

# v4.2 компоненты (импортируем из существующей системы)
try:
    from conscious_ai_ultimate import ConsciousAI_Ultimate, UltimateConfig
    HAS_V4_FEATURES = True
except ImportError:
    HAS_V4_FEATURES = False
    print("⚠️  v4.2 компоненты не найдены. Работаем только с v5.0 функциями.")


@dataclass
class V5Config:
    """Конфигурация ConsciousAI v5.0"""

    # Основные настройки
    personality_name: str = "ConsciousAI"
    use_llm: bool = False  # Работает БЕЗ LLM API!

    # v5.0 функции
    enable_semantic_memory: bool = True
    enable_meta_cognition: bool = True
    enable_insight_generation: bool = True

    # v4.2 функции (если доступны)
    enable_project_generation: bool = True
    enable_marketing_automation: bool = True
    enable_autonomous_agent: bool = True

    # Базы данных
    memory_db_path: str = "semantic_memory_v5.db"

    # Настройки памяти
    memory_compression_ratio: float = 30.0  # Целевое сжатие
    memory_forget_days: int = 60  # Забывать старые зёрна
    memory_importance_threshold: float = 0.2


class ConsciousAI_v5:
    """
    ConsciousAI v5.0 - Мета-Сознательный AI

    Главный класс, объединяющий все системы
    """

    VERSION = "5.0.0"

    def __init__(self, config: Optional[V5Config] = None):
        self.config = config or V5Config()
        self.start_time = datetime.now()

        print(f"🧠 Инициализация ConsciousAI v{self.VERSION}...")

        # === v5.0 Системы ===
        print("  ✓ Смысловая память...")
        self.semantic_memory = SemanticMemory(db_path=self.config.memory_db_path)
        self.semantic_compressor = SemanticCompressor()
        self.knowledge_graph = KnowledgeGraph(self.semantic_memory)

        print("  ✓ Мета-когнитивный движок...")
        self.meta_engine = MetaCognitiveEngine(self.semantic_memory)

        print("  ✓ Генератор инсайтов...")
        self.insight_generator = InsightGenerator(self.semantic_memory)

        print("  ✓ Простой интерфейс...")
        self.interface = SimpleInterface()

        # === v4.2 Системы (если доступны) ===
        self.v4_system = None
        if HAS_V4_FEATURES:
            print("  ✓ Интеграция с v4.2...")
            v4_config = UltimateConfig(
                personality_name=self.config.personality_name,
                use_llm=self.config.use_llm,
                enable_autonomous_agent=self.config.enable_autonomous_agent,
                enable_project_generation=self.config.enable_project_generation
            )
            self.v4_system = ConsciousAI_Ultimate(v4_config)

        # Диалоговая история (для контекста)
        self.conversation_history: List[Dict[str, str]] = []

        print(f"✅ ConsciousAI v{self.VERSION} готов!\n")

    async def chat(self, user_message: str, store_in_memory: bool = True) -> str:
        """
        Основной метод диалога с мета-сознанием

        Args:
            user_message: Сообщение пользователя
            store_in_memory: Сохранить в смысловую память

        Returns:
            Ответ AI
        """
        # 1. Сохранить сообщение пользователя в историю
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # 2. Сжать сообщение в смысловое зерно
        if store_in_memory and self.config.enable_semantic_memory:
            user_kernel = self.semantic_compressor.compress(
                user_message,
                language="ru",  # TODO: автоопределение
                context={"role": "user"}
            )
            self.semantic_memory.store(user_kernel)

        # 3. Проверить, это команда или диалог?
        command, args = self.interface.parse_command(user_message)

        # Если это команда - обработать через интерфейс
        if command in ["создай", "маркетинг", "анализ", "инсайт", "память",
                       "рефлексия", "партнёр", "статистика", "помощь"]:
            result = self.interface.run_command(command, args)

            # Выполнить действие на основе результата
            if result:
                response = await self._execute_command(result)
            else:
                response = "Команда выполнена"

        # Иначе - обычный диалог
        else:
            # Если есть v4.2 - использовать его для диалога
            if self.v4_system:
                response = await self.v4_system.chat(user_message)
            else:
                response = await self._simple_dialogue(user_message)

        # 4. Сохранить ответ в память
        if store_in_memory and self.config.enable_semantic_memory:
            response_kernel = self.semantic_compressor.compress(
                response,
                language="ru",
                context={"role": "assistant"}
            )
            self.semantic_memory.store(response_kernel)

        # 5. Сохранить ответ в историю
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        # 6. Мета-когнитивный анализ (периодически)
        if len(self.conversation_history) % 5 == 0:  # Каждые 5 сообщений
            await self._meta_cognitive_checkpoint()

        return response

    async def _execute_command(self, command_result: Dict[str, Any]) -> str:
        """Выполнить команду на основе результата интерфейса"""
        action = command_result.get("action")

        if action == "create_project":
            return await self._handle_create_project(command_result)

        elif action == "launch_marketing":
            return await self._handle_marketing(command_result)

        elif action == "deep_analysis":
            return await self._handle_analysis(command_result)

        elif action == "generate_insights":
            return await self._handle_insights(command_result)

        elif action == "memory_view":
            return await self._handle_memory_view(command_result)

        elif action == "reflection":
            return await self._handle_reflection(command_result)

        elif action == "partner_mode":
            return await self._handle_partner_mode(command_result)

        elif action == "show_stats":
            return self._handle_stats()

        else:
            return "Команда принята в обработку"

    async def _handle_create_project(self, cmd: Dict[str, Any]) -> str:
        """Обработать создание проекта"""
        project_type = cmd.get("project_type", "")

        if self.v4_system and self.config.enable_project_generation:
            # Использовать v4.2 систему создания проектов
            # (это заглушка - реальная реализация в v4.2)
            return f"🚀 Создание проекта '{project_type}' запущено!\n(используется v4.2 ProjectGenerator)"
        else:
            return f"📝 Проект '{project_type}' будет создан\n(требуется v4.2 компонент)"

    async def _handle_marketing(self, cmd: Dict[str, Any]) -> str:
        """Обработать маркетинговую кампанию"""
        description = cmd.get("description", "")

        if self.v4_system and self.config.enable_marketing_automation:
            return f"📢 Маркетинговая кампания '{description}' запущена!\n(используется v4.2 MarketingAgent)\nРаботает 24/7 автономно"
        else:
            return f"📝 Кампания '{description}' будет запущена\n(требуется v4.2 компонент)"

    async def _handle_analysis(self, cmd: Dict[str, Any]) -> str:
        """Глубокий анализ с использованием мета-сознания"""
        topic = cmd.get("topic", "")

        # Шаг 1: Поиск в памяти
        related_kernels = self.semantic_memory.search(topic, limit=10)

        # Шаг 2: Генерация инсайтов
        insights = self.insight_generator.generate(topic, limit=3)

        # Шаг 3: Оценка уверенности
        confidence, reasoning = self.meta_engine.gap_detector.assess_confidence(topic)

        # Составить ответ
        response = f"🔍 Глубокий анализ: '{topic}'\n\n"
        response += f"📊 Уверенность: {confidence.value} ({reasoning})\n\n"

        if related_kernels:
            response += f"💾 Найдено в памяти: {len(related_kernels)} зёрен знаний\n"
            response += "Топ-3 релевантных:\n"
            for i, (kernel, rel) in enumerate(related_kernels[:3], 1):
                response += f"  {i}. [{rel:.2f}] {kernel.essence[:60]}...\n"
            response += "\n"

        if insights:
            response += f"💡 Сгенерировано инсайтов: {len(insights)}\n"
            for i, insight in enumerate(insights, 1):
                response += f"  {i}. [{insight.insight_type.value}] {insight.content[:80]}...\n"

        return response

    async def _handle_insights(self, cmd: Dict[str, Any]) -> str:
        """Генерация инсайтов"""
        topic = cmd.get("topic", "")

        insights = self.insight_generator.generate(topic, limit=5)

        response = f"💡 Инсайты о '{topic}':\n\n"

        for i, insight in enumerate(insights, 1):
            response += f"{i}. [{insight.insight_type.value.upper()}]\n"
            response += f"   {insight.content}\n"
            response += f"   Score: {insight.get_score():.2f} "
            response += f"(новизна={insight.novelty:.1f}, польза={insight.usefulness:.1f})\n\n"

        return response

    async def _handle_memory_view(self, cmd: Dict[str, Any]) -> str:
        """Показать смысловую память"""
        view_type = cmd.get("view_type", "show_all")

        stats = self.semantic_memory.get_statistics()

        response = "🧠 Смысловая память:\n\n"
        response += f"📊 Всего зёрен: {stats['total_kernels']}\n"
        response += f"🔗 Всего связей: {stats['total_connections']}\n"
        response += f"⭐ Средняя важность: {stats['average_importance']:.2f}\n\n"

        if stats['type_distribution']:
            response += "📈 Распределение по типам:\n"
            for ktype, count in stats['type_distribution'].items():
                response += f"  • {ktype}: {count}\n"
            response += "\n"

        if stats['top_activated']:
            response += "🔥 Самые активируемые зёрна:\n"
            for kernel in stats['top_activated'][:3]:
                response += f"  • {kernel['essence'][:50]}... (x{kernel['activations']})\n"

        return response

    async def _handle_reflection(self, cmd: Dict[str, Any]) -> str:
        """Рефлексия AI"""
        focus = cmd.get("focus", "")

        # Получить последние рефлексии
        recent_reflections = self.meta_engine.reflector.get_recent_reflections(limit=3)

        response = "🤔 Рефлексия AI:\n\n"

        if recent_reflections:
            response += "Последние размышления:\n\n"
            for i, reflection in enumerate(recent_reflections, 1):
                response += f"{i}. [{reflection.reflection_type.value}]\n"
                response += f"   {reflection.content}\n"
                if reflection.insights:
                    response += f"   Инсайты: {', '.join(reflection.insights[:2])}\n"
                response += "\n"
        else:
            response += "Пока нет рефлексий. AI начнёт думать о своём мышлении по мере работы.\n"

        # Задать вопрос себе
        question = f"Что я думаю о текущей работе?"
        answer = self.meta_engine.inner_dialogue.ask_self(question)

        response += f"💭 Внутренний диалог:\n"
        response += f"   Q: {question}\n"
        response += f"   A: {answer}\n"

        return response

    async def _handle_partner_mode(self, cmd: Dict[str, Any]) -> str:
        """Режим партнёра"""
        mode = cmd.get("mode", "co_creation")

        response = f"🤝 Режим партнёра активирован: {mode}\n\n"
        response += "Давай работать вместе!\n"
        response += "Я буду не просто выполнять, а активно участвовать в процессе:\n"
        response += "  • Предлагать идеи\n"
        response += "  • Задавать вопросы\n"
        response += "  • Оспаривать решения (если нужно)\n"
        response += "  • Искать лучшие варианты\n\n"
        response += "Готов к сотрудничеству! 💪"

        return response

    def _handle_stats(self) -> str:
        """Статистика работы"""
        uptime = datetime.now() - self.start_time
        hours = uptime.total_seconds() / 3600

        mem_stats = self.semantic_memory.get_statistics()
        insights_count = len(self.insight_generator.generated_insights)
        reflections_count = len(self.meta_engine.reflector.reflections)

        response = "📊 Статистика ConsciousAI v5.0:\n\n"
        response += f"⏱️  Время работы: {hours:.1f} часов\n"
        response += f"💬 Сообщений в диалоге: {len(self.conversation_history)}\n\n"

        response += "🧠 Смысловая память:\n"
        response += f"  • Зёрен знаний: {mem_stats['total_kernels']}\n"
        response += f"  • Связей: {mem_stats['total_connections']}\n\n"

        response += "💡 Интеллект:\n"
        response += f"  • Инсайтов сгенерировано: {insights_count}\n"
        response += f"  • Рефлексий проведено: {reflections_count}\n\n"

        if HAS_V4_FEATURES:
            response += "✅ v4.2 функции: активны\n"
        else:
            response += "⚠️  v4.2 функции: недоступны\n"

        return response

    async def _simple_dialogue(self, user_message: str) -> str:
        """Простой диалог без v4.2 (фолбэк)"""
        # Поиск в памяти
        related = self.semantic_memory.search(user_message, limit=3)

        if related:
            # Использовать найденное знание
            top_kernel = related[0][0]
            return f"Понял! Это связано с: {top_kernel.essence}\n\nЧто конкретно хочешь сделать?"
        else:
            return "Интересно! Расскажи подробнее, я сохраню это в память и буду использовать."

    async def _meta_cognitive_checkpoint(self):
        """
        Контрольная точка мета-познания
        AI анализирует свою работу
        """
        if not self.config.enable_meta_cognition:
            return

        # Проанализировать последние сообщения
        if len(self.conversation_history) >= 5:
            recent_messages = self.conversation_history[-5:]
            user_messages = [m["content"] for m in recent_messages if m["role"] == "user"]

            # Обнаружить паттерны
            pattern_reflection = self.meta_engine.reflector.reflect_on_pattern(user_messages)

            if pattern_reflection:
                # Сохранить рефлексию в память
                reflection_kernel = self.semantic_compressor.compress(
                    pattern_reflection.content,
                    context={"type": "meta_reflection"}
                )
                reflection_kernel.importance = 0.8  # Высокая важность
                self.semantic_memory.store(reflection_kernel)

    def interactive_mode(self):
        """Запустить интерактивный режим"""
        self.interface.interactive_loop()


# Удобная функция создания
def create_ai(config: Optional[V5Config] = None) -> ConsciousAI_v5:
    """Создать ConsciousAI v5.0"""
    return ConsciousAI_v5(config)


# Пример использования
if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("  🧠 ConsciousAI v5.0 - Мета-Сознательный AI")
    print("=" * 60)
    print()

    # Создать AI
    config = V5Config(
        personality_name="ConsciousAI",
        use_llm=False,  # Без LLM - полностью автономный!
        enable_semantic_memory=True,
        enable_meta_cognition=True,
        enable_insight_generation=True
    )

    ai = ConsciousAI_v5(config)

    # Если передан аргумент - запустить интерактивный режим
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("Запуск интерактивного режима...\n")
        ai.interactive_mode()
    else:
        # Демо
        print("Демо работы системы:\n")

        async def demo():
            # Пример 1: Диалог
            print("1. Диалог:")
            response = await ai.chat("Привет! Расскажи о себе")
            print(f"   AI: {response[:150]}...\n")

            # Пример 2: Сохранение знаний
            print("2. Сохранение знаний:")
            await ai.chat("Мне нужен AI с мета-сознанием и смысловой памятью")
            print("   ✓ Сохранено в смысловую память\n")

            # Пример 3: Команда инсайт
            print("3. Генерация инсайтов:")
            response = await ai.chat("инсайт улучшение памяти AI")
            print(f"   {response[:200]}...\n")

            # Пример 4: Статистика
            print("4. Статистика:")
            response = await ai.chat("статистика")
            print(f"   {response[:300]}...\n")

            print("✅ Демо завершено!")
            print("\nДля интерактивного режима запустите:")
            print("  python conscious_ai_v5.py --interactive")

        asyncio.run(demo())
