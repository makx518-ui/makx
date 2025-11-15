"""
ConsciousAI v5.0 - Meta-Cognitive Engine
Мета-когнитивный движок - AI, который осознаёт своё мышление

Компоненты:
1. Reflector - рефлексия (думает о своих мыслях)
2. SelfEvaluator - самооценка (анализирует качество решений)
3. GapDetector - детектор пробелов (знает, что не знает)
4. LearningPlanner - планировщик обучения (учится на опыте)
5. InnerDialogue - внутренний диалог (обсуждение с собой)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import json

from semantic_kernel import SemanticKernel, KernelType, SemanticCompressor
from semantic_memory import SemanticMemory


class ReflectionType(Enum):
    """Типы рефлексии"""
    THOUGHT = "thought"              # Мысль о мысли
    DECISION = "decision"            # Анализ решения
    PATTERN = "pattern"              # Обнаружение паттерна
    MISTAKE = "mistake"              # Признание ошибки
    INSIGHT = "insight"              # Озарение
    QUESTION = "question"            # Вопрос к себе


class ConfidenceLevel(Enum):
    """Уровни уверенности"""
    CERTAIN = 1.0        # Уверен на 100%
    HIGH = 0.8           # Высокая уверенность
    MEDIUM = 0.5         # Средняя уверенность
    LOW = 0.3            # Низкая уверенность
    UNCERTAIN = 0.1      # Неуверен


@dataclass
class Reflection:
    """
    Рефлексия - размышление о собственном мышлении

    Пример:
    "Я заметил, что пользователь всегда просит 'немедленно' - это паттерн.
     Мне нужно быстрее переходить к действию, меньше спрашивать."
    """
    reflection_type: ReflectionType
    content: str
    confidence: float
    triggered_by: Optional[str] = None  # Что вызвало рефлексию
    insights: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.reflection_type.value,
            "content": self.content,
            "confidence": self.confidence,
            "triggered_by": self.triggered_by,
            "insights": self.insights,
            "action_items": self.action_items,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class QualityMetrics:
    """Метрики качества решения"""
    correctness: float = 0.5      # Правильность (0-1)
    completeness: float = 0.5     # Полнота (0-1)
    efficiency: float = 0.5       # Эффективность (0-1)
    clarity: float = 0.5          # Ясность (0-1)
    overall_score: float = 0.5    # Общая оценка (0-1)

    def calculate_overall(self):
        """Вычислить общую оценку"""
        self.overall_score = (
            self.correctness * 0.4 +
            self.completeness * 0.3 +
            self.efficiency * 0.2 +
            self.clarity * 0.1
        )
        return self.overall_score


@dataclass
class KnowledgeGap:
    """Пробел в знаниях"""
    topic: str
    description: str
    importance: float
    detected_at: datetime = field(default_factory=datetime.now)
    learning_strategy: Optional[str] = None


class Reflector:
    """
    Рефлектор - думает о своих мыслях

    Примеры рефлексии:
    - "Почему я выбрал этот подход?"
    - "Что я мог сделать лучше?"
    - "Какой паттерн я вижу в действиях пользователя?"
    """

    def __init__(self, memory: SemanticMemory):
        self.memory = memory
        self.reflections: List[Reflection] = []

    def reflect_on_decision(self, decision: str, context: Dict[str, Any]) -> Reflection:
        """
        Рефлексия о принятом решении

        Args:
            decision: Описание решения
            context: Контекст принятия решения

        Returns:
            Reflection объект
        """
        # Найти похожие решения в памяти
        similar_decisions = self.memory.search(
            decision,
            limit=5,
            kernel_types=[KernelType.DECISION]
        )

        # Проанализировать
        insights = []
        confidence = 0.5

        if similar_decisions:
            insights.append(f"Похожих решений найдено: {len(similar_decisions)}")

            # Проверить, были ли успешные похожие решения
            successful_count = sum(
                1 for k, _ in similar_decisions
                if k.metadata.get("success", False)
            )

            if successful_count > len(similar_decisions) / 2:
                insights.append("Подобные решения обычно успешны")
                confidence = 0.8
            else:
                insights.append("Осторожно: подобные решения иногда проблемны")
                confidence = 0.4

        # Создать рефлексию
        reflection = Reflection(
            reflection_type=ReflectionType.DECISION,
            content=f"Решение: {decision}",
            confidence=confidence,
            triggered_by="decision_making",
            insights=insights,
            action_items=["Отслеживать результат", "Сравнить с похожими случаями"]
        )

        self.reflections.append(reflection)
        return reflection

    def reflect_on_pattern(self, observations: List[str]) -> Optional[Reflection]:
        """
        Обнаружить паттерн в наблюдениях

        Args:
            observations: Список наблюдений

        Returns:
            Reflection если паттерн найден
        """
        # Простой анализ: найти повторяющиеся ключевые слова
        word_counts = {}
        for obs in observations:
            words = obs.lower().split()
            for word in words:
                if len(word) > 4:  # Игнорировать короткие слова
                    word_counts[word] = word_counts.get(word, 0) + 1

        # Найти часто встречающиеся слова
        frequent_words = [
            word for word, count in word_counts.items()
            if count >= len(observations) * 0.5  # В 50%+ наблюдений
        ]

        if frequent_words:
            pattern_description = f"Обнаружен паттерн: частые слова {frequent_words}"

            reflection = Reflection(
                reflection_type=ReflectionType.PATTERN,
                content=pattern_description,
                confidence=0.7,
                triggered_by="pattern_detection",
                insights=[
                    f"Слова '{', '.join(frequent_words)}' появляются часто",
                    "Это может указывать на важные темы"
                ],
                action_items=[
                    "Учесть этот паттерн в будущих ответах",
                    "Приоритезировать связанные темы"
                ]
            )

            self.reflections.append(reflection)
            return reflection

        return None

    def reflect_on_mistake(self, mistake: str, correction: str) -> Reflection:
        """
        Рефлексия об ошибке

        Args:
            mistake: Описание ошибки
            correction: Как исправили

        Returns:
            Reflection объект
        """
        reflection = Reflection(
            reflection_type=ReflectionType.MISTAKE,
            content=f"Ошибка: {mistake}",
            confidence=0.9,  # Уверены, что это ошибка
            triggered_by="error_detection",
            insights=[
                f"Исправление: {correction}",
                "Важно избегать подобных ошибок в будущем"
            ],
            action_items=[
                "Добавить проверку перед подобными операциями",
                "Обновить паттерны избегания ошибок"
            ]
        )

        self.reflections.append(reflection)

        # Сохранить в память как важный урок
        compressor = SemanticCompressor()
        lesson_kernel = compressor.compress(
            f"Урок: {mistake} -> {correction}",
            context={"is_lesson": True, "mistake": mistake}
        )
        lesson_kernel.importance = 0.9  # Высокая важность
        self.memory.store(lesson_kernel)

        return reflection

    def get_recent_reflections(self, limit: int = 10) -> List[Reflection]:
        """Получить последние рефлексии"""
        return self.reflections[-limit:]


class SelfEvaluator:
    """
    Самооценщик - оценивает качество своих решений

    Вопросы:
    - "Насколько хорошо я справился?"
    - "Что можно было сделать лучше?"
    - "Доволен ли пользователь результатом?"
    """

    def evaluate_response(
        self,
        user_query: str,
        ai_response: str,
        context: Optional[Dict] = None
    ) -> QualityMetrics:
        """
        Оценить качество ответа

        Args:
            user_query: Запрос пользователя
            ai_response: Ответ AI
            context: Дополнительный контекст

        Returns:
            QualityMetrics с оценками
        """
        metrics = QualityMetrics()

        # 1. Правильность (есть ли ответ на вопрос?)
        # Простая эвристика: проверить наличие ключевых слов из запроса
        query_words = set(user_query.lower().split())
        response_words = set(ai_response.lower().split())
        overlap = len(query_words & response_words)
        metrics.correctness = min(overlap / max(len(query_words), 1), 1.0)

        # 2. Полнота (достаточно ли информации?)
        # Эвристика: длина ответа
        min_length = 50
        optimal_length = 200
        response_length = len(ai_response)

        if response_length < min_length:
            metrics.completeness = response_length / min_length
        elif response_length <= optimal_length:
            metrics.completeness = 1.0
        else:
            # Слишком длинный ответ - снижаем оценку
            metrics.completeness = max(0.7, optimal_length / response_length)

        # 3. Эффективность (быстро ли решена задача?)
        # Если в контексте есть время выполнения
        if context and "execution_time" in context:
            exec_time = context["execution_time"]
            if exec_time < 1.0:
                metrics.efficiency = 1.0
            elif exec_time < 5.0:
                metrics.efficiency = 0.8
            else:
                metrics.efficiency = 0.5
        else:
            metrics.efficiency = 0.7  # По умолчанию

        # 4. Ясность (понятен ли ответ?)
        # Эвристика: отсутствие слишком длинных предложений
        sentences = ai_response.split('.')
        avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)

        if avg_sentence_length < 100:
            metrics.clarity = 1.0
        elif avg_sentence_length < 200:
            metrics.clarity = 0.7
        else:
            metrics.clarity = 0.5

        # Вычислить общую оценку
        metrics.calculate_overall()

        return metrics

    def evaluate_code_quality(self, code: str) -> QualityMetrics:
        """
        Оценить качество сгенерированного кода

        Args:
            code: Код для оценки

        Returns:
            QualityMetrics
        """
        metrics = QualityMetrics()

        # 1. Правильность (синтаксис)
        try:
            compile(code, '<string>', 'exec')
            metrics.correctness = 1.0
        except SyntaxError:
            metrics.correctness = 0.3

        # 2. Полнота (есть ли docstrings, комментарии?)
        has_docstrings = '"""' in code or "'''" in code
        has_comments = '#' in code
        metrics.completeness = 0.5
        if has_docstrings:
            metrics.completeness += 0.3
        if has_comments:
            metrics.completeness += 0.2

        # 3. Эффективность (короткий код лучше)
        lines = code.strip().split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        if len(code_lines) < 50:
            metrics.efficiency = 1.0
        elif len(code_lines) < 100:
            metrics.efficiency = 0.8
        else:
            metrics.efficiency = 0.6

        # 4. Ясность (читаемость)
        # Проверить наличие хороших практик
        has_type_hints = ':' in code and '->' in code
        has_meaningful_names = not any(
            bad in code for bad in ['x =', 'y =', 'temp =', 'tmp =']
        )

        metrics.clarity = 0.5
        if has_type_hints:
            metrics.clarity += 0.25
        if has_meaningful_names:
            metrics.clarity += 0.25

        metrics.calculate_overall()
        return metrics


class GapDetector:
    """
    Детектор пробелов - находит пробелы в знаниях

    Принцип: "Знание о незнании - это тоже знание"
    """

    def __init__(self, memory: SemanticMemory):
        self.memory = memory
        self.known_gaps: List[KnowledgeGap] = []

    def detect_gaps(self, topic: str) -> List[KnowledgeGap]:
        """
        Обнаружить пробелы в знаниях по теме

        Args:
            topic: Тема для анализа

        Returns:
            Список обнаруженных пробелов
        """
        # Поискать в памяти информацию по теме
        related_kernels = self.memory.search(topic, limit=20)

        # Если мало информации - это пробел
        if len(related_kernels) < 3:
            gap = KnowledgeGap(
                topic=topic,
                description=f"Недостаточно знаний о '{topic}'",
                importance=0.7,
                learning_strategy="Собрать больше информации через диалог или поиск"
            )
            self.known_gaps.append(gap)
            return [gap]

        # Проанализировать полноту (есть ли разные типы зёрен?)
        kernel_types = set(k.kernel_type for k, _ in related_kernels)
        expected_types = {KernelType.FACT, KernelType.INSIGHT, KernelType.DECISION}

        missing_types = expected_types - kernel_types

        gaps = []
        if missing_types:
            for missing_type in missing_types:
                gap = KnowledgeGap(
                    topic=f"{topic} ({missing_type.value})",
                    description=f"Нет {missing_type.value} о '{topic}'",
                    importance=0.5,
                    learning_strategy=f"Получить {missing_type.value} через опыт или обучение"
                )
                gaps.append(gap)
                self.known_gaps.append(gap)

        return gaps

    def assess_confidence(self, topic: str) -> Tuple[ConfidenceLevel, str]:
        """
        Оценить уверенность в знаниях по теме

        Args:
            topic: Тема

        Returns:
            (ConfidenceLevel, reasoning)
        """
        related_kernels = self.memory.search(topic, limit=10)

        # Мало информации = низкая уверенность
        if len(related_kernels) == 0:
            return (
                ConfidenceLevel.UNCERTAIN,
                f"Нет информации о '{topic}'"
            )
        elif len(related_kernels) < 3:
            return (
                ConfidenceLevel.LOW,
                f"Мало информации о '{topic}' ({len(related_kernels)} зёрен)"
            )
        elif len(related_kernels) < 7:
            return (
                ConfidenceLevel.MEDIUM,
                f"Умеренное количество информации о '{topic}'"
            )
        elif len(related_kernels) < 15:
            return (
                ConfidenceLevel.HIGH,
                f"Много информации о '{topic}'"
            )
        else:
            return (
                ConfidenceLevel.CERTAIN,
                f"Очень много информации о '{topic}' ({len(related_kernels)} зёрен)"
            )


class LearningPlanner:
    """
    Планировщик обучения - планирует, как заполнить пробелы

    Стратегии:
    - Активное обучение (задавать вопросы)
    - Обучение на опыте (пробовать и учиться на ошибках)
    - Обучение через аналогии (применять знания из других областей)
    """

    def create_learning_plan(self, gaps: List[KnowledgeGap]) -> Dict[str, Any]:
        """
        Создать план обучения для заполнения пробелов

        Args:
            gaps: Список пробелов

        Returns:
            План обучения
        """
        # Отсортировать по важности
        sorted_gaps = sorted(gaps, key=lambda g: g.importance, reverse=True)

        plan = {
            "total_gaps": len(gaps),
            "priority_gaps": [],
            "strategies": [],
            "estimated_effort": "medium"
        }

        for gap in sorted_gaps[:5]:  # Топ-5 важных
            plan["priority_gaps"].append({
                "topic": gap.topic,
                "importance": gap.importance,
                "strategy": gap.learning_strategy or "Общее изучение"
            })

            # Определить стратегию
            if "опыт" in gap.learning_strategy.lower():
                plan["strategies"].append("experiential_learning")
            else:
                plan["strategies"].append("active_inquiry")

        # Оценить усилия
        if len(gaps) > 10:
            plan["estimated_effort"] = "high"
        elif len(gaps) > 5:
            plan["estimated_effort"] = "medium"
        else:
            plan["estimated_effort"] = "low"

        return plan


class InnerDialogue:
    """
    Внутренний диалог - AI обсуждает с самим собой

    Примеры:
    Q: "Почему пользователь просит 'немедленно'?"
    A: "Возможно, он ценит скорость. Или у него срочный проект."
    Q: "Как я могу работать быстрее?"
    A: "Меньше спрашивать, больше делать. Проактивный подход."
    """

    def __init__(self):
        self.dialogue_history: List[Dict[str, str]] = []

    def ask_self(self, question: str) -> str:
        """
        Задать вопрос самому себе

        Args:
            question: Вопрос

        Returns:
            Ответ (самоанализ)
        """
        # Простая эвристика для самоответов
        answer = self._generate_self_answer(question)

        self.dialogue_history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })

        return answer

    def _generate_self_answer(self, question: str) -> str:
        """Сгенерировать ответ на вопрос к себе"""
        question_lower = question.lower()

        # Простые паттерны
        if "почему" in question_lower:
            return "Возможно, потому что это важно для цели или соответствует паттерну поведения."

        if "как" in question_lower:
            return "Можно попробовать разбить на шаги или использовать известные паттерны."

        if "что" in question_lower:
            return "Нужно проанализировать контекст и выбрать наиболее подходящий вариант."

        return "Требуется больше информации для точного ответа."

    def get_dialogue(self, limit: int = 10) -> List[Dict[str, str]]:
        """Получить историю внутреннего диалога"""
        return self.dialogue_history[-limit:]


class MetaCognitiveEngine:
    """
    Мета-когнитивный движок - объединяет все компоненты

    Главный интерфейс для мета-сознания
    """

    def __init__(self, memory: SemanticMemory):
        self.memory = memory
        self.reflector = Reflector(memory)
        self.evaluator = SelfEvaluator()
        self.gap_detector = GapDetector(memory)
        self.learning_planner = LearningPlanner()
        self.inner_dialogue = InnerDialogue()

    def think_about_thinking(self, thought: str) -> Dict[str, Any]:
        """
        Мета-мышление - думать о своём мышлении

        Args:
            thought: Мысль для анализа

        Returns:
            Результат мета-анализа
        """
        result = {
            "original_thought": thought,
            "reflection": None,
            "quality": None,
            "gaps": [],
            "learning_plan": None,
            "inner_dialogue": []
        }

        # 1. Рефлексия
        reflection = self.reflector.reflect_on_decision(thought, {})
        result["reflection"] = reflection.to_dict()

        # 2. Самооценка качества мысли
        quality = self.evaluator.evaluate_response("", thought)
        result["quality"] = {
            "overall": quality.overall_score,
            "completeness": quality.completeness,
            "clarity": quality.clarity
        }

        # 3. Обнаружение пробелов
        gaps = self.gap_detector.detect_gaps(thought)
        result["gaps"] = [
            {"topic": g.topic, "importance": g.importance}
            for g in gaps
        ]

        # 4. План обучения
        if gaps:
            result["learning_plan"] = self.learning_planner.create_learning_plan(gaps)

        # 5. Внутренний диалог
        question = f"Что я думаю о: {thought[:50]}...?"
        answer = self.inner_dialogue.ask_self(question)
        result["inner_dialogue"] = [
            {"question": question, "answer": answer}
        ]

        return result


# Пример использования
if __name__ == "__main__":
    print("🧠 Meta-Cognitive Engine - Мета-сознание\n")

    # Создать память и движок
    memory = SemanticMemory(db_path="test_metacog.db")
    engine = MetaCognitiveEngine(memory)

    # Пример 1: Рефлексия о решении
    print("Пример 1: Рефлексия")
    decision = "Решил создать семантическую память для сжатия контекста"
    reflection = engine.reflector.reflect_on_decision(decision, {})
    print(f"  Решение: {decision}")
    print(f"  Уверенность: {reflection.confidence}")
    print(f"  Инсайты: {reflection.insights}\n")

    # Пример 2: Самооценка
    print("Пример 2: Самооценка")
    response = "Создал модуль semantic_memory.py с поддержкой графа знаний и ассоциативного поиска"
    quality = engine.evaluator.evaluate_response("", response)
    print(f"  Ответ: {response}")
    print(f"  Оценка: {quality.overall_score:.2f}")
    print(f"  Полнота: {quality.completeness:.2f}")
    print(f"  Ясность: {quality.clarity:.2f}\n")

    # Пример 3: Обнаружение пробелов
    print("Пример 3: Обнаружение пробелов")
    gaps = engine.gap_detector.detect_gaps("квантовые вычисления")
    for gap in gaps:
        print(f"  Пробел: {gap.topic}")
        print(f"  Важность: {gap.importance}")
        print(f"  Стратегия: {gap.learning_strategy}\n")

    # Пример 4: Мета-мышление
    print("Пример 4: Мета-мышление")
    thought = "Нужно создать простой интуитивный интерфейс для управления AI"
    meta_result = engine.think_about_thinking(thought)
    print(f"  Мысль: {thought}")
    print(f"  Качество мысли: {meta_result['quality']['overall']:.2f}")
    print(f"  Обнаружено пробелов: {len(meta_result['gaps'])}")
    if meta_result['learning_plan']:
        print(f"  План обучения: {meta_result['learning_plan']['estimated_effort']} усилий")

    print("\n✅ Мета-когнитивный движок работает!")
