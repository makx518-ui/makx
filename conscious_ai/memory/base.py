"""
ConsciousAI - Базовые абстракции для памяти
Интерфейсы для различных хранилищ

Рекомендация GPT-5: Создать базовый интерфейс MemoryStore
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid


class KernelType(Enum):
    """Типы смысловых зёрен"""
    FACT = "fact"
    INSIGHT = "insight"
    DECISION = "decision"
    PATTERN = "pattern"
    GOAL = "goal"
    RELATIONSHIP = "relationship"
    PREFERENCE = "preference"
    CONTEXT = "context"
    EMOTION = "emotion"
    REFLECTION = "reflection"


@dataclass
class SemanticKernel:
    """
    Универсальная структура смыслового зерна

    Рекомендация GPT-5: Использовать pydantic
    TODO: Перевести на pydantic в следующей итерации
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    essence: str = ""
    concepts: List[str] = field(default_factory=list)
    kernel_type: KernelType = KernelType.FACT
    importance: float = 0.5
    connections: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    activation_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Новые поля по рекомендации GPT-5
    ttl: Optional[int] = None  # Time-to-live в секундах
    priority: int = 0  # Приоритет (0-10)
    tags: List[str] = field(default_factory=list)  # Теги для быстрого поиска
    source: str = "user"  # Источник информации

    def activate(self):
        """Активировать зерно (увеличить счётчик)"""
        self.activation_count += 1
        self.last_accessed = datetime.now()

    def is_expired(self) -> bool:
        """Проверить истёк ли TTL"""
        if self.ttl is None:
            return False
        elapsed = (datetime.now() - self.timestamp).total_seconds()
        return elapsed > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация"""
        data = asdict(self)
        data['kernel_type'] = self.kernel_type.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticKernel':
        """Десериализация"""
        data = data.copy()
        data['kernel_type'] = KernelType(data['kernel_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('last_accessed'):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


@dataclass
class SearchQuery:
    """
    Структура поискового запроса

    Рекомендация GPT-5: Добавить фильтрацию и scoring
    """
    text: str = ""
    concepts: List[str] = field(default_factory=list)
    kernel_types: Optional[List[KernelType]] = None
    min_importance: float = 0.0
    max_importance: float = 1.0
    min_priority: int = 0
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    limit: int = 10
    offset: int = 0
    include_expired: bool = False
    sort_by: str = "relevance"  # relevance, importance, timestamp, activation
    sort_order: str = "desc"


@dataclass
class SearchResult:
    """Результат поиска"""
    kernel: SemanticKernel
    score: float  # Релевантность 0-1
    match_reason: str = ""


class BaseMemoryStore(ABC):
    """
    Абстрактный базовый класс для хранилища памяти

    Рекомендация GPT-5: Все реализации должны наследовать этот интерфейс

    Методы:
        save() - сохранить зерно
        get() - получить по ID
        search() - поиск по запросу
        delete() - удалить
        update() - обновить
        stats() - статистика
    """

    @abstractmethod
    def save(self, kernel: SemanticKernel) -> str:
        """
        Сохранить семантическое зерно

        Args:
            kernel: Зерно для сохранения

        Returns:
            ID сохранённого зерна

        Raises:
            MemoryStorageError: При ошибке сохранения
        """
        pass

    @abstractmethod
    def get(self, kernel_id: str, activate: bool = True) -> Optional[SemanticKernel]:
        """
        Получить зерно по ID

        Args:
            kernel_id: ID зерна
            activate: Увеличить счётчик активаций

        Returns:
            SemanticKernel или None

        Raises:
            MemoryRetrievalError: При ошибке чтения
        """
        pass

    @abstractmethod
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Поиск зёрен по запросу

        Args:
            query: Структура поискового запроса

        Returns:
            Список SearchResult отсортированный по score

        Raises:
            MemoryRetrievalError: При ошибке поиска
        """
        pass

    @abstractmethod
    def delete(self, kernel_id: str) -> bool:
        """
        Удалить зерно

        Args:
            kernel_id: ID зерна

        Returns:
            True если удалено, False если не найдено
        """
        pass

    @abstractmethod
    def update(self, kernel: SemanticKernel) -> bool:
        """
        Обновить существующее зерно

        Args:
            kernel: Зерно с обновлёнными данными

        Returns:
            True если обновлено, False если не найдено
        """
        pass

    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """
        Получить статистику хранилища

        Returns:
            Словарь со статистикой:
            - total_kernels: int
            - by_type: Dict[str, int]
            - avg_importance: float
            - total_connections: int
            - storage_size_bytes: int
        """
        pass

    @abstractmethod
    def cleanup(self, days_old: int = 30, importance_threshold: float = 0.2) -> int:
        """
        Очистить старые неважные зёрна

        Args:
            days_old: Удалить старше N дней
            importance_threshold: Удалить с важностью ниже порога

        Returns:
            Количество удалённых зёрен
        """
        pass

    def save_batch(self, kernels: List[SemanticKernel]) -> List[str]:
        """
        Сохранить несколько зёрен (batch операция)

        Args:
            kernels: Список зёрен

        Returns:
            Список ID сохранённых зёрен

        По умолчанию - последовательное сохранение.
        Переопределить для оптимизации.
        """
        return [self.save(k) for k in kernels]

    def get_batch(self, kernel_ids: List[str]) -> List[SemanticKernel]:
        """
        Получить несколько зёрен (batch операция)

        Args:
            kernel_ids: Список ID

        Returns:
            Список найденных зёрен
        """
        results = []
        for kid in kernel_ids:
            kernel = self.get(kid, activate=False)
            if kernel:
                results.append(kernel)
        return results

    def connect(self, kernel_id1: str, kernel_id2: str, strength: float = 1.0) -> bool:
        """
        Создать связь между зёрнами

        Args:
            kernel_id1: ID первого зерна
            kernel_id2: ID второго зерна
            strength: Сила связи (0-1)

        Returns:
            True если связь создана
        """
        kernel1 = self.get(kernel_id1, activate=False)
        kernel2 = self.get(kernel_id2, activate=False)

        if not kernel1 or not kernel2:
            return False

        # Добавить связи (двунаправленно)
        if kernel_id2 not in kernel1.connections:
            kernel1.connections.append(kernel_id2)
            self.update(kernel1)

        if kernel_id1 not in kernel2.connections:
            kernel2.connections.append(kernel_id1)
            self.update(kernel2)

        return True

    def get_connected(self, kernel_id: str) -> List[SemanticKernel]:
        """
        Получить все связанные зёрна

        Args:
            kernel_id: ID зерна

        Returns:
            Список связанных зёрен
        """
        kernel = self.get(kernel_id, activate=False)
        if not kernel:
            return []

        return self.get_batch(kernel.connections)


class InMemoryStore(BaseMemoryStore):
    """
    In-memory реализация для тестирования

    Быстрая, но не персистентная
    """

    def __init__(self):
        self._storage: Dict[str, SemanticKernel] = {}

    def save(self, kernel: SemanticKernel) -> str:
        self._storage[kernel.id] = kernel
        return kernel.id

    def get(self, kernel_id: str, activate: bool = True) -> Optional[SemanticKernel]:
        kernel = self._storage.get(kernel_id)
        if kernel and activate:
            kernel.activate()
        return kernel

    def search(self, query: SearchQuery) -> List[SearchResult]:
        results = []

        for kernel in self._storage.values():
            # Пропустить истёкшие
            if not query.include_expired and kernel.is_expired():
                continue

            # Фильтры
            if kernel.importance < query.min_importance:
                continue
            if kernel.importance > query.max_importance:
                continue
            if kernel.priority < query.min_priority:
                continue
            if query.kernel_types and kernel.kernel_type not in query.kernel_types:
                continue
            if query.tags and not set(query.tags).intersection(set(kernel.tags)):
                continue
            if query.source and kernel.source != query.source:
                continue

            # Вычислить score
            score = self._calculate_score(query, kernel)
            if score > 0:
                results.append(SearchResult(
                    kernel=kernel,
                    score=score,
                    match_reason=f"Score: {score:.2f}"
                ))

        # Сортировка
        if query.sort_by == "relevance":
            results.sort(key=lambda r: r.score, reverse=query.sort_order == "desc")
        elif query.sort_by == "importance":
            results.sort(key=lambda r: r.kernel.importance, reverse=query.sort_order == "desc")
        elif query.sort_by == "timestamp":
            results.sort(key=lambda r: r.kernel.timestamp, reverse=query.sort_order == "desc")
        elif query.sort_by == "activation":
            results.sort(key=lambda r: r.kernel.activation_count, reverse=query.sort_order == "desc")

        # Пагинация
        return results[query.offset:query.offset + query.limit]

    def _calculate_score(self, query: SearchQuery, kernel: SemanticKernel) -> float:
        """Вычислить релевантность"""
        score = 0.0

        # Совпадение текста
        if query.text:
            text_lower = query.text.lower()
            if text_lower in kernel.essence.lower():
                score += 0.5
            # Слова из запроса в концепциях
            query_words = set(text_lower.split())
            kernel_concepts = set(c.lower() for c in kernel.concepts)
            overlap = len(query_words.intersection(kernel_concepts))
            if query_words:
                score += (overlap / len(query_words)) * 0.3

        # Совпадение концепций
        if query.concepts:
            query_concepts = set(c.lower() for c in query.concepts)
            kernel_concepts = set(c.lower() for c in kernel.concepts)
            overlap = len(query_concepts.intersection(kernel_concepts))
            if query_concepts:
                score += (overlap / len(query_concepts)) * 0.2

        # Бонус за важность
        score += kernel.importance * 0.1

        return min(score, 1.0)

    def delete(self, kernel_id: str) -> bool:
        if kernel_id in self._storage:
            del self._storage[kernel_id]
            return True
        return False

    def update(self, kernel: SemanticKernel) -> bool:
        if kernel.id in self._storage:
            self._storage[kernel.id] = kernel
            return True
        return False

    def stats(self) -> Dict[str, Any]:
        total = len(self._storage)
        by_type = {}
        total_importance = 0.0
        total_connections = 0

        for kernel in self._storage.values():
            type_name = kernel.kernel_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            total_importance += kernel.importance
            total_connections += len(kernel.connections)

        return {
            "total_kernels": total,
            "by_type": by_type,
            "avg_importance": total_importance / total if total > 0 else 0,
            "total_connections": total_connections // 2,  # Двунаправленные
            "storage_size_bytes": 0  # In-memory
        }

    def cleanup(self, days_old: int = 30, importance_threshold: float = 0.2) -> int:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days_old)
        to_delete = []

        for kid, kernel in self._storage.items():
            if kernel.importance < importance_threshold and kernel.timestamp < cutoff:
                to_delete.append(kid)

        for kid in to_delete:
            del self._storage[kid]

        return len(to_delete)


# Пример использования
if __name__ == "__main__":
    print("🧠 Тест базовых абстракций памяти:\n")

    # Создать in-memory хранилище
    store = InMemoryStore()

    # Создать и сохранить зёрна
    kernel1 = SemanticKernel(
        essence="AI с мета-сознанием",
        concepts=["ai", "мета", "сознание"],
        kernel_type=KernelType.GOAL,
        importance=0.9,
        priority=10,
        tags=["core", "vision"]
    )

    kernel2 = SemanticKernel(
        essence="Смысловая память сжимает контекст",
        concepts=["память", "сжатие", "контекст"],
        kernel_type=KernelType.FACT,
        importance=0.7,
        tags=["memory"]
    )

    # Сохранить
    id1 = store.save(kernel1)
    id2 = store.save(kernel2)
    print(f"✅ Сохранено 2 зерна")

    # Поиск
    query = SearchQuery(
        text="мета-сознание",
        min_importance=0.5,
        limit=5
    )

    results = store.search(query)
    print(f"\n🔍 Поиск 'мета-сознание':")
    for res in results:
        print(f"  Score: {res.score:.2f} | {res.kernel.essence}")

    # Связать
    store.connect(id1, id2)
    print(f"\n🔗 Создана связь между зёрнами")

    # Статистика
    stats = store.stats()
    print(f"\n📊 Статистика:")
    print(f"  Всего зёрен: {stats['total_kernels']}")
    print(f"  По типам: {stats['by_type']}")
    print(f"  Связей: {stats['total_connections']}")

    print("\n✅ Базовые абстракции работают!")
