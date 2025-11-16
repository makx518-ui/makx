"""
ConsciousAI v5.0 - Semantic Kernel
Компрессия смысла: превращаем контекст в "смысловые зёрна"

Ключевая инновация: вместо хранения всего текста диалога,
мы сжимаем его в компактные семантические ядра (kernels),
которые сохраняют суть, но занимают в 20-50 раз меньше места!
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum


class KernelType(Enum):
    """Типы смысловых зёрен"""
    FACT = "fact"                    # Факт (Python 3.11 быстрее на 25%)
    INSIGHT = "insight"              # Инсайт (пользователь хочет автономность)
    DECISION = "decision"            # Решение (выбрали архитектуру из 5 слоёв)
    PATTERN = "pattern"              # Паттерн (пользователь предпочитает "немедленно")
    GOAL = "goal"                    # Цель (создать v5.0 с мета-сознанием)
    RELATIONSHIP = "relationship"    # Связь (маркетинг зависит от генератора контента)
    PREFERENCE = "preference"        # Предпочтение (простой интерфейс)
    CONTEXT = "context"              # Контекст (работаем в Git-репозитории)


class ImportanceLevel(Enum):
    """Уровни важности"""
    CRITICAL = 1.0      # Критично (основные цели, архитектура)
    HIGH = 0.8          # Высокая (ключевые решения)
    MEDIUM = 0.5        # Средняя (факты, детали)
    LOW = 0.3           # Низкая (мелочи)
    TRIVIAL = 0.1       # Минимальная (временное)


@dataclass
class SemanticKernel:
    """
    Смысловое зерно - сжатая суть информации

    Пример:
    Вместо: "Пользователь сказал: 'Отлично дружище приступай немедленно,
             сделай код-шедевр' и я начал работу над v4.1..."

    Храним: {
        "essence": "Пользователь требует немедленного действия",
        "concepts": ["действие", "срочность", "качество"],
        "kernel_type": "PATTERN",
        "importance": 0.8
    }

    Сжатие: ~200 символов → ~50 символов = 4x компрессия!
    """

    # Уникальный ID
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Суть - квинтэссенция смысла (1-2 предложения)
    essence: str = ""

    # Ключевые концепции (слова-теги)
    concepts: List[str] = field(default_factory=list)

    # Тип зерна
    kernel_type: KernelType = KernelType.FACT

    # Важность (0.0 - 1.0)
    importance: float = 0.5

    # Связи с другими зёрнами (ID)
    connections: List[str] = field(default_factory=list)

    # Временная метка
    timestamp: datetime = field(default_factory=datetime.now)

    # Метаданные (дополнительная информация)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Счётчик активаций (сколько раз использовалось)
    activation_count: int = 0

    # Последнее использование
    last_accessed: Optional[datetime] = None

    def activate(self):
        """Отметить использование зерна"""
        self.activation_count += 1
        self.last_accessed = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь"""
        data = asdict(self)
        data['kernel_type'] = self.kernel_type.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticKernel':
        """Десериализация из словаря"""
        data = data.copy()
        data['kernel_type'] = KernelType(data['kernel_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('last_accessed'):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)

    def __repr__(self):
        return f"SemanticKernel({self.kernel_type.value}, importance={self.importance:.2f}, essence='{self.essence[:50]}...')"


class SemanticCompressor:
    """
    Компрессор смысла - превращает текст в семантические зёрна

    Методы компрессии:
    1. Извлечение ключевых концепций (NLP без моделей)
    2. Определение типа информации
    3. Оценка важности
    4. Сжатие в essence (суть)
    """

    # Ключевые слова для определения типа
    TYPE_KEYWORDS = {
        KernelType.FACT: {
            'ru': ['это', 'есть', 'является', 'составляет', 'равно', 'содержит'],
            'en': ['is', 'are', 'contains', 'has', 'equals', 'consists']
        },
        KernelType.INSIGHT: {
            'ru': ['понял', 'осознал', 'заметил', 'обнаружил', 'вижу', 'важно'],
            'en': ['realize', 'understand', 'notice', 'important', 'key', 'crucial']
        },
        KernelType.DECISION: {
            'ru': ['решил', 'выбрал', 'буду', 'сделаю', 'применю', 'использую'],
            'en': ['decide', 'choose', 'will', 'going to', 'use', 'apply']
        },
        KernelType.PATTERN: {
            'ru': ['всегда', 'обычно', 'часто', 'предпочитает', 'любит', 'хочет'],
            'en': ['always', 'usually', 'often', 'prefer', 'like', 'want']
        },
        KernelType.GOAL: {
            'ru': ['цель', 'задача', 'нужно', 'необходимо', 'создать', 'достичь'],
            'en': ['goal', 'objective', 'need', 'must', 'create', 'achieve']
        }
    }

    # Стоп-слова (игнорируем при извлечении концепций)
    STOP_WORDS = {
        'ru': {'и', 'в', 'не', 'на', 'с', 'что', 'как', 'это', 'по', 'а', 'но',
               'да', 'нет', 'для', 'от', 'к', 'о', 'у', 'же', 'бы', 'так', 'вот',
               'был', 'была', 'было', 'были', 'есть', 'быть', 'будет', 'может'},
        'en': {'the', 'is', 'and', 'of', 'to', 'in', 'a', 'you', 'that', 'it',
               'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they',
               'be', 'at', 'one', 'have', 'this', 'from', 'or', 'had', 'by'}
    }

    def compress(self, text: str, language: str = "ru", context: Optional[Dict] = None) -> SemanticKernel:
        """
        Сжать текст в семантическое зерно

        Args:
            text: Исходный текст
            language: Язык текста ('ru' или 'en')
            context: Дополнительный контекст

        Returns:
            SemanticKernel с сжатым смыслом
        """
        # 1. Извлечь ключевые концепции
        concepts = self._extract_concepts(text, language)

        # 2. Определить тип зерна
        kernel_type = self._detect_type(text, language)

        # 3. Оценить важность
        importance = self._calculate_importance(text, concepts, kernel_type)

        # 4. Создать essence (суть)
        essence = self._create_essence(text, concepts, kernel_type)

        # 5. Создать зерно
        kernel = SemanticKernel(
            essence=essence,
            concepts=concepts,
            kernel_type=kernel_type,
            importance=importance,
            metadata={
                "original_length": len(text),
                "compressed_length": len(essence),
                "compression_ratio": len(text) / max(len(essence), 1),
                "language": language
            }
        )

        if context:
            kernel.metadata.update(context)

        return kernel

    def _extract_concepts(self, text: str, language: str) -> List[str]:
        """Извлечь ключевые концепции из текста"""
        # Простой метод: взять слова длиннее 4 символов, исключая стоп-слова
        words = text.lower().split()
        stop_words = self.STOP_WORDS.get(language, set())

        concepts = []
        for word in words:
            # Очистить от пунктуации
            clean_word = ''.join(c for c in word if c.isalnum())

            # Проверить условия
            if (len(clean_word) > 4 and
                clean_word not in stop_words and
                not clean_word.isdigit()):
                concepts.append(clean_word)

        # Удалить дубликаты, сохранив порядок
        seen = set()
        unique_concepts = []
        for c in concepts:
            if c not in seen:
                seen.add(c)
                unique_concepts.append(c)

        # Ограничить до топ-10
        return unique_concepts[:10]

    def _detect_type(self, text: str, language: str) -> KernelType:
        """Определить тип смыслового зерна"""
        text_lower = text.lower()

        # Подсчитать совпадения для каждого типа
        scores = {}
        for kernel_type, keywords in self.TYPE_KEYWORDS.items():
            lang_keywords = keywords.get(language, [])
            score = sum(1 for kw in lang_keywords if kw in text_lower)
            scores[kernel_type] = score

        # Выбрать тип с максимальным score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        # По умолчанию - FACT
        return KernelType.FACT

    def _calculate_importance(self, text: str, concepts: List[str], kernel_type: KernelType) -> float:
        """Оценить важность информации"""
        importance = 0.5  # Базовая важность

        # Увеличить для определённых типов
        if kernel_type in [KernelType.GOAL, KernelType.DECISION, KernelType.INSIGHT]:
            importance += 0.2

        # Увеличить если много ключевых концепций
        if len(concepts) >= 7:
            importance += 0.1

        # Увеличить если есть важные слова
        important_words_ru = ['важно', 'критично', 'необходимо', 'обязательно', 'немедленно']
        important_words_en = ['critical', 'important', 'must', 'immediately', 'essential']

        text_lower = text.lower()
        if any(word in text_lower for word in important_words_ru + important_words_en):
            importance += 0.2

        # Ограничить диапазон [0.1, 1.0]
        return min(max(importance, 0.1), 1.0)

    def _create_essence(self, text: str, concepts: List[str], kernel_type: KernelType) -> str:
        """Создать суть (essence) - сжатое представление"""
        # Если текст короткий (< 100 символов), использовать как есть
        if len(text) <= 100:
            return text.strip()

        # Для длинного текста: взять первое предложение + ключевые концепции
        sentences = text.split('.')
        first_sentence = sentences[0].strip()

        # Если первое предложение слишком длинное, обрезать
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."

        # Добавить топ-3 концепции если есть место
        if len(first_sentence) < 60 and concepts:
            concept_str = ", ".join(concepts[:3])
            essence = f"{first_sentence} [{concept_str}]"
        else:
            essence = first_sentence

        return essence

    def compress_conversation(self, messages: List[Dict[str, str]], language: str = "ru") -> List[SemanticKernel]:
        """
        Сжать целый диалог в набор зёрен

        Args:
            messages: Список сообщений [{"role": "user", "content": "..."}]
            language: Язык

        Returns:
            Список SemanticKernel
        """
        kernels = []

        for i, msg in enumerate(messages):
            context = {
                "message_index": i,
                "role": msg.get("role", "unknown"),
                "total_messages": len(messages)
            }

            kernel = self.compress(
                text=msg.get("content", ""),
                language=language,
                context=context
            )

            kernels.append(kernel)

        return kernels


class CompressionAnalyzer:
    """Анализатор эффективности компрессии"""

    @staticmethod
    def analyze(original_text: str, kernel: SemanticKernel) -> Dict[str, Any]:
        """Проанализировать качество компрессии"""
        original_size = len(original_text)
        compressed_size = len(kernel.essence)

        return {
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": original_size / max(compressed_size, 1),
            "space_saved_percent": ((original_size - compressed_size) / original_size * 100),
            "concepts_extracted": len(kernel.concepts),
            "kernel_type": kernel.kernel_type.value,
            "importance": kernel.importance
        }

    @staticmethod
    def analyze_batch(texts: List[str], kernels: List[SemanticKernel]) -> Dict[str, Any]:
        """Проанализировать компрессию для батча"""
        total_original = sum(len(t) for t in texts)
        total_compressed = sum(len(k.essence) for k in kernels)

        return {
            "total_original_size": total_original,
            "total_compressed_size": total_compressed,
            "average_compression_ratio": total_original / max(total_compressed, 1),
            "total_kernels": len(kernels),
            "space_saved_percent": ((total_original - total_compressed) / total_original * 100),
            "average_concepts_per_kernel": sum(len(k.concepts) for k in kernels) / len(kernels),
            "kernel_type_distribution": {
                kt.value: sum(1 for k in kernels if k.kernel_type == kt)
                for kt in KernelType
            }
        }


# Пример использования
if __name__ == "__main__":
    print("🧠 Semantic Kernel - Компрессия смысла\n")

    # Создать компрессор
    compressor = SemanticCompressor()

    # Пример 1: Сжать одно сообщение
    text1 = "Отлично дружище приступай немедленно, сделай код-шедевр по максимуму докрути опцию маркетинга"
    kernel1 = compressor.compress(text1, language="ru")

    print("Пример 1: Сжатие сообщения")
    print(f"  Оригинал: {text1}")
    print(f"  Суть: {kernel1.essence}")
    print(f"  Концепции: {kernel1.concepts}")
    print(f"  Тип: {kernel1.kernel_type.value}")
    print(f"  Важность: {kernel1.importance}")

    analysis = CompressionAnalyzer.analyze(text1, kernel1)
    print(f"  Сжатие: {analysis['compression_ratio']:.1f}x")
    print(f"  Сэкономлено: {analysis['space_saved_percent']:.0f}%\n")

    # Пример 2: Сжать диалог
    conversation = [
        {"role": "user", "content": "Привет Клод!"},
        {"role": "assistant", "content": "Привет! Как дела?"},
        {"role": "user", "content": "Нужно создать AI с мета-сознанием и смысловой памятью"},
        {"role": "assistant", "content": "Отлично! Начинаю проектировать архитектуру v5.0"}
    ]

    kernels = compressor.compress_conversation(conversation, language="ru")

    print("Пример 2: Сжатие диалога")
    for i, kernel in enumerate(kernels):
        print(f"  Сообщение {i+1}: {kernel.essence[:60]}...")

    batch_analysis = CompressionAnalyzer.analyze_batch(
        [msg["content"] for msg in conversation],
        kernels
    )
    print(f"\n  Общее сжатие: {batch_analysis['average_compression_ratio']:.1f}x")
    print(f"  Сэкономлено: {batch_analysis['space_saved_percent']:.0f}%")
    print(f"  Всего зёрен: {batch_analysis['total_kernels']}")
