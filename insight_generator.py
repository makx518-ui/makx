"""
ConsciousAI v5.0 - Insight Generator
Генератор инсайтов - создание озарений через синтез знаний

Методы:
1. Аналогии - находить паттерны из других областей
2. Синтез - объединять несвязанные идеи
3. Латеральное мышление - нестандартные связи
4. Абстракция - поднятие на уровень выше
5. Инверсия - противоположный подход
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import random

from semantic_kernel import SemanticKernel, KernelType
from semantic_memory import SemanticMemory, KnowledgeGraph


class InsightType(Enum):
    """Типы инсайтов"""
    ANALOGY = "analogy"              # Аналогия из другой области
    SYNTHESIS = "synthesis"          # Синтез идей
    LATERAL = "lateral"              # Латеральное мышление
    ABSTRACTION = "abstraction"      # Абстракция (выше уровень)
    INVERSION = "inversion"          # Инверсия (противоположное)
    PATTERN = "pattern"              # Обнаружение паттерна
    CONTRADICTION = "contradiction"  # Противоречие → новое понимание


@dataclass
class Insight:
    """
    Инсайт - озарение, новое понимание

    Пример:
    "Семантическая память похожа на ZIP-архив для смысла:
     сжимает информацию без потери сути!"
    """
    insight_type: InsightType
    content: str
    source_concepts: List[str]
    confidence: float
    novelty: float  # Насколько новое (0-1)
    usefulness: float  # Насколько полезное (0-1)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_score(self) -> float:
        """Общая оценка инсайта"""
        return (
            self.confidence * 0.3 +
            self.novelty * 0.4 +
            self.usefulness * 0.3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.insight_type.value,
            "content": self.content,
            "source_concepts": self.source_concepts,
            "confidence": self.confidence,
            "novelty": self.novelty,
            "usefulness": self.usefulness,
            "score": self.get_score(),
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class AnalogyFinder:
    """
    Поиск аналогий - находит похожие паттерны в других областях

    Пример:
    Задача: "Как сжать память AI?"
    Аналогия: "Как ZIP сжимает файлы? Находит повторяющиеся паттерны!"
    Инсайт: "Можно сжимать смысл, находя повторяющиеся концепции!"
    """

    # Домены знаний
    KNOWLEDGE_DOMAINS = [
        "технологии",
        "природа",
        "биология",
        "физика",
        "архитектура",
        "музыка",
        "спорт",
        "медицина",
        "психология",
        "экономика",
        "искусство",
        "история"
    ]

    # Известные аналогии
    COMMON_ANALOGIES = {
        "сжатие": {
            "технологии": "ZIP-архив сжимает файлы, находя повторения",
            "природа": "ДНК сжимает инструкции для организма в компактный код",
            "психология": "Память человека сжимает опыт в ключевые воспоминания"
        },
        "поиск": {
            "природа": "Пчёлы ищут цветы по запаху и танцу",
            "технологии": "Google ищет страницы по индексу и релевантности",
            "биология": "Иммунная система ищет патогены по антителам"
        },
        "связи": {
            "природа": "Мицелий грибов связывает деревья в лесу",
            "технологии": "Интернет связывает компьютеры в сеть",
            "социология": "Социальные сети связывают людей"
        },
        "обучение": {
            "биология": "Нейроны обучаются через усиление синапсов",
            "спорт": "Мышечная память через повторение",
            "технологии": "AI обучается на примерах"
        }
    }

    def find_analogies(
        self,
        concept: str,
        target_domain: Optional[str] = None
    ) -> List[Tuple[str, str, float]]:
        """
        Найти аналогии для концепции

        Args:
            concept: Концепция для поиска аналогий
            target_domain: Целевой домен (опционально)

        Returns:
            Список (домен, аналогия, уверенность)
        """
        analogies = []

        # Найти в известных аналогиях
        concept_lower = concept.lower()
        for key, domains in self.COMMON_ANALOGIES.items():
            if key in concept_lower:
                for domain, analogy in domains.items():
                    if target_domain is None or domain == target_domain:
                        analogies.append((domain, analogy, 0.8))

        # Если не нашли, создать общие аналогии
        if not analogies:
            for domain in self.KNOWLEDGE_DOMAINS[:3]:  # Топ-3 домена
                analogy = f"В области '{domain}' {concept} может работать аналогично известным паттернам"
                analogies.append((domain, analogy, 0.3))

        return analogies

    def create_analogy_insight(
        self,
        problem: str,
        source_domain: str,
        analogy: str
    ) -> Insight:
        """
        Создать инсайт на основе аналогии

        Args:
            problem: Проблема
            source_domain: Домен-источник аналогии
            analogy: Описание аналогии

        Returns:
            Insight объект
        """
        content = f"Аналогия из '{source_domain}': {analogy}\n→ Применение к '{problem}'"

        return Insight(
            insight_type=InsightType.ANALOGY,
            content=content,
            source_concepts=[problem, source_domain],
            confidence=0.7,
            novelty=0.6,
            usefulness=0.7,
            metadata={
                "source_domain": source_domain,
                "analogy": analogy
            }
        )


class SynthesisEngine:
    """
    Движок синтеза - объединяет несвязанные идеи

    Пример:
    Идея 1: "Смысловая память сжимает контекст"
    Идея 2: "Граф связывает концепции"
    Синтез: "Граф смысловых зёрен = сжатая память + связи!"
    """

    def synthesize(
        self,
        ideas: List[str],
        memory: Optional[SemanticMemory] = None
    ) -> Insight:
        """
        Синтезировать новую идею из нескольких

        Args:
            ideas: Список идей для синтеза
            memory: Семантическая память (для контекста)

        Returns:
            Insight с синтезированной идеей
        """
        if len(ideas) < 2:
            raise ValueError("Нужно минимум 2 идеи для синтеза")

        # Извлечь ключевые концепции из каждой идеи
        all_concepts = []
        for idea in ideas:
            words = idea.lower().split()
            concepts = [w for w in words if len(w) > 4][:3]  # Топ-3 слова
            all_concepts.extend(concepts)

        # Создать синтезированное описание
        synthesis_content = f"Синтез идей:\n"
        for i, idea in enumerate(ideas, 1):
            synthesis_content += f"  {i}. {idea}\n"

        synthesis_content += f"\n→ Новое понимание: "

        # Простая эвристика синтеза
        if len(ideas) == 2:
            synthesis_content += f"Объединяя '{ideas[0][:30]}...' и '{ideas[1][:30]}...', "
            synthesis_content += f"получаем комбинированное решение, которое использует преимущества обоих подходов"
        else:
            synthesis_content += f"Комбинация {len(ideas)} идей создаёт многогранное решение"

        return Insight(
            insight_type=InsightType.SYNTHESIS,
            content=synthesis_content,
            source_concepts=all_concepts,
            confidence=0.6,
            novelty=0.7,
            usefulness=0.8,
            metadata={"original_ideas": ideas}
        )


class LateralThinker:
    """
    Латеральное мышление - нестандартные связи

    Методы:
    - Случайные входы (random input)
    - Провокация (что если наоборот?)
    - Скачки концепций (concept jumping)
    """

    def __init__(self, memory: SemanticMemory):
        self.memory = memory

    def random_input(self, problem: str) -> Insight:
        """
        Метод случайного входа - добавить случайную концепцию

        Args:
            problem: Проблема для решения

        Returns:
            Insight с нестандартной идеей
        """
        # Случайные концепции для стимуляции мышления
        random_concepts = [
            "игра", "музыка", "природа", "вода", "огонь",
            "танец", "цвет", "запах", "время", "пространство",
            "зеркало", "дверь", "мост", "река", "гора"
        ]

        random_concept = random.choice(random_concepts)

        content = f"Латеральное мышление: '{problem}' + случайная концепция '{random_concept}'\n\n"
        content += f"Что если подойти к '{problem}' как к '{random_concept}'?\n"

        # Создать связь
        if random_concept == "музыка":
            content += "→ Может быть, нужна гармония компонентов? Ритм работы?"
        elif random_concept == "природа":
            content += "→ Может быть, использовать органический рост? Адаптацию?"
        elif random_concept == "вода":
            content += "→ Может быть, нужна текучесть? Адаптация к форме?"
        elif random_concept == "игра":
            content += "→ Может быть, добавить элементы игры? Правила и свободу?"
        else:
            content += f"→ Исследовать свойства '{random_concept}' для новых идей"

        return Insight(
            insight_type=InsightType.LATERAL,
            content=content,
            source_concepts=[problem, random_concept],
            confidence=0.4,  # Низкая уверенность - это экспериментально
            novelty=0.9,     # Высокая новизна
            usefulness=0.5,   # Средняя полезность
            metadata={"method": "random_input", "random_concept": random_concept}
        )

    def provocation(self, statement: str) -> Insight:
        """
        Метод провокации - перевернуть утверждение

        Args:
            statement: Утверждение

        Returns:
            Insight с провокационной идеей
        """
        content = f"Провокация: '{statement}'\n\n"
        content += "Что если НАОБОРОТ?\n"
        content += f"→ Противоположный подход может открыть новые возможности:\n"
        content += "  • Вместо сложного → простое\n"
        content += "  • Вместо быстрого → медленное, но глубокое\n"
        content += "  • Вместо большого → маленькое, но точечное\n"
        content += "  • Вместо автоматического → ручное с контролем\n"

        return Insight(
            insight_type=InsightType.LATERAL,
            content=content,
            source_concepts=[statement],
            confidence=0.5,
            novelty=0.8,
            usefulness=0.6,
            metadata={"method": "provocation"}
        )

    def concept_jumping(self, start_concept: str, jumps: int = 3) -> Insight:
        """
        Скачки концепций - перепрыгивать между идеями

        Args:
            start_concept: Начальная концепция
            jumps: Количество скачков

        Returns:
            Insight с цепочкой концепций
        """
        # Найти связанные концепции в памяти
        search_results = self.memory.search(start_concept, limit=jumps * 2)

        concept_chain = [start_concept]

        for kernel, _ in search_results[:jumps]:
            # Взять первую концепцию из зерна
            if kernel.concepts:
                concept_chain.append(kernel.concepts[0])

        content = f"Скачки концепций (от '{start_concept}'):\n\n"
        for i, concept in enumerate(concept_chain):
            content += f"  {i+1}. {concept}\n"

        content += f"\n→ Финальная концепция '{concept_chain[-1]}' может дать свежий взгляд на '{start_concept}'"

        return Insight(
            insight_type=InsightType.LATERAL,
            content=content,
            source_concepts=concept_chain,
            confidence=0.5,
            novelty=0.7,
            usefulness=0.6,
            metadata={"method": "concept_jumping", "chain": concept_chain}
        )


class AbstractionEngine:
    """
    Движок абстракции - поднятие на уровень выше

    Примеры:
    "Создать веб-сайт" → "Создать онлайн-присутствие"
    "Написать код" → "Решить проблему"
    "Оптимизировать алгоритм" → "Улучшить производительность"
    """

    # Уровни абстракции
    ABSTRACTION_LEVELS = {
        "создать сайт": [
            "Создать онлайн-присутствие",
            "Обеспечить доступ к информации",
            "Решить коммуникационную задачу"
        ],
        "написать код": [
            "Решить проблему",
            "Автоматизировать процесс",
            "Создать инструмент"
        ],
        "обучить AI": [
            "Передать знания",
            "Улучшить способности",
            "Развить интеллект"
        ]
    }

    def abstract(self, concrete_task: str, levels: int = 2) -> Insight:
        """
        Абстрагировать задачу на уровни выше

        Args:
            concrete_task: Конкретная задача
            levels: Сколько уровней подняться

        Returns:
            Insight с абстрактным пониманием
        """
        # Найти в известных абстракциях
        abstractions = []
        task_lower = concrete_task.lower()

        for key, abstract_list in self.ABSTRACTION_LEVELS.items():
            if key in task_lower:
                abstractions = abstract_list[:levels]
                break

        # Если не нашли, создать общую абстракцию
        if not abstractions:
            abstractions = [
                f"Решить задачу на более высоком уровне",
                f"Достичь цели через '{concrete_task}'"
            ]

        content = f"Абстракция задачи '{concrete_task}':\n\n"
        for i, abstract in enumerate(abstractions, 1):
            content += f"  Уровень {i}: {abstract}\n"

        content += f"\n→ На высшем уровне это о: {abstractions[-1]}"

        return Insight(
            insight_type=InsightType.ABSTRACTION,
            content=content,
            source_concepts=[concrete_task] + abstractions,
            confidence=0.7,
            novelty=0.5,
            usefulness=0.7,
            metadata={"abstractions": abstractions}
        )


class PatternDetector:
    """
    Детектор паттернов - находит повторяющиеся структуры

    В данных, поведении, коде, диалогах
    """

    def detect_in_sequence(self, sequence: List[Any]) -> Optional[Insight]:
        """
        Обнаружить паттерн в последовательности

        Args:
            sequence: Последовательность элементов

        Returns:
            Insight если паттерн найден
        """
        if len(sequence) < 3:
            return None

        # Простой метод: найти повторения
        from collections import Counter
        counter = Counter(sequence)

        # Есть ли элементы, повторяющиеся 50%+ раз?
        threshold = len(sequence) * 0.5
        repeating = [item for item, count in counter.items() if count >= threshold]

        if repeating:
            content = f"Обнаружен паттерн в последовательности:\n\n"
            content += f"Элементы {repeating} повторяются в {len(sequence)} элементах\n"
            content += f"→ Это указывает на устойчивый паттерн поведения"

            return Insight(
                insight_type=InsightType.PATTERN,
                content=content,
                source_concepts=["паттерн", "повторение"],
                confidence=0.8,
                novelty=0.4,
                usefulness=0.8,
                metadata={"pattern": repeating, "sequence_length": len(sequence)}
            )

        return None


class InsightGenerator:
    """
    Генератор инсайтов - главный класс

    Объединяет все методы генерации инсайтов
    """

    def __init__(self, memory: SemanticMemory):
        self.memory = memory
        self.analogy_finder = AnalogyFinder()
        self.synthesis_engine = SynthesisEngine()
        self.lateral_thinker = LateralThinker(memory)
        self.abstraction_engine = AbstractionEngine()
        self.pattern_detector = PatternDetector()
        self.generated_insights: List[Insight] = []

    def generate(
        self,
        topic: str,
        methods: Optional[List[InsightType]] = None,
        limit: int = 5
    ) -> List[Insight]:
        """
        Генерировать инсайты по теме

        Args:
            topic: Тема для инсайтов
            methods: Методы генерации (если None - все)
            limit: Максимум инсайтов

        Returns:
            Список инсайтов, отсортированных по score
        """
        insights = []

        # Определить методы
        if methods is None:
            methods = [
                InsightType.ANALOGY,
                InsightType.SYNTHESIS,
                InsightType.LATERAL,
                InsightType.ABSTRACTION
            ]

        # Генерировать инсайты разными методами
        if InsightType.ANALOGY in methods:
            analogies = self.analogy_finder.find_analogies(topic)
            for domain, analogy, conf in analogies[:2]:
                insight = self.analogy_finder.create_analogy_insight(
                    topic, domain, analogy
                )
                insights.append(insight)

        if InsightType.LATERAL in methods:
            lateral = self.lateral_thinker.random_input(topic)
            insights.append(lateral)

        if InsightType.ABSTRACTION in methods:
            abstract = self.abstraction_engine.abstract(topic)
            insights.append(abstract)

        if InsightType.SYNTHESIS in methods:
            # Найти связанные идеи в памяти
            related = self.memory.search(topic, limit=3)
            if len(related) >= 2:
                ideas = [k.essence for k, _ in related]
                synthesis = self.synthesis_engine.synthesize(ideas)
                insights.append(synthesis)

        # Сохранить сгенерированные инсайты
        self.generated_insights.extend(insights)

        # Отсортировать по score и ограничить
        insights.sort(key=lambda i: i.get_score(), reverse=True)

        return insights[:limit]

    def get_best_insights(self, limit: int = 10) -> List[Insight]:
        """Получить лучшие инсайты всех времён"""
        sorted_insights = sorted(
            self.generated_insights,
            key=lambda i: i.get_score(),
            reverse=True
        )
        return sorted_insights[:limit]


# Пример использования
if __name__ == "__main__":
    print("💡 Insight Generator - Генератор инсайтов\n")

    # Создать память и генератор
    memory = SemanticMemory(db_path="test_insights.db")
    generator = InsightGenerator(memory)

    # Добавить некоторые знания в память
    from semantic_kernel import SemanticCompressor
    compressor = SemanticCompressor()

    knowledge = [
        "Смысловая память сжимает контекст в семантические зёрна",
        "Граф связывает зёрна между собой",
        "Ассоциативный поиск находит релевантные зёрна",
        "Мета-когнитивный движок анализирует собственное мышление"
    ]

    for k in knowledge:
        kernel = compressor.compress(k, language="ru")
        memory.store(kernel)

    # Пример 1: Генерация инсайтов
    print("Пример 1: Генерация инсайтов")
    topic = "как улучшить память AI"
    insights = generator.generate(topic, limit=3)

    for i, insight in enumerate(insights, 1):
        print(f"\n  Инсайт {i} [{insight.insight_type.value}]:")
        print(f"  {insight.content[:150]}...")
        print(f"  Score: {insight.get_score():.2f} (новизна={insight.novelty:.2f}, польза={insight.usefulness:.2f})")

    # Пример 2: Аналогии
    print("\n\nПример 2: Поиск аналогий")
    analogies = generator.analogy_finder.find_analogies("сжатие данных")
    for domain, analogy, conf in analogies[:2]:
        print(f"\n  [{domain}]: {analogy}")

    # Пример 3: Латеральное мышление
    print("\n\nПример 3: Латеральное мышление")
    lateral = generator.lateral_thinker.random_input("создать простой интерфейс")
    print(f"  {lateral.content[:200]}...")

    print("\n✅ Генератор инсайтов работает!")
