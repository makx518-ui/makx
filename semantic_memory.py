"""
ConsciousAI v5.0 - Semantic Memory
Смысловая память - хранилище семантических зёрен

Ключевые возможности:
- Хранение зёрен в граф-структуре
- Ассоциативный поиск
- Автоматическое связывание похожих зёрен
- Векторное сходство без тяжёлых моделей
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import math

from semantic_kernel import SemanticKernel, KernelType, SemanticCompressor


class SemanticMemory:
    """
    Смысловая память - граф семантических зёрен

    Функции:
    1. Хранение зёрен
    2. Поиск по смыслу (ассоциативный поиск)
    3. Автоматическое связывание похожих зёрен
    4. Управление важностью (забывание неважного)
    """

    def __init__(self, db_path: str = "semantic_memory.db"):
        self.db_path = db_path
        self.compressor = SemanticCompressor()
        self._init_database()

    def _init_database(self):
        """Инициализировать базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица зёрен
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kernels (
                id TEXT PRIMARY KEY,
                essence TEXT NOT NULL,
                concepts TEXT NOT NULL,
                kernel_type TEXT NOT NULL,
                importance REAL NOT NULL,
                timestamp TEXT NOT NULL,
                activation_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                metadata TEXT
            )
        ''')

        # Таблица связей между зёрнами
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                kernel_id TEXT NOT NULL,
                connected_kernel_id TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                connection_type TEXT,
                created_at TEXT NOT NULL,
                PRIMARY KEY (kernel_id, connected_kernel_id),
                FOREIGN KEY (kernel_id) REFERENCES kernels(id),
                FOREIGN KEY (connected_kernel_id) REFERENCES kernels(id)
            )
        ''')

        # Индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON kernels(importance DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON kernels(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON kernels(kernel_type)')

        conn.commit()
        conn.close()

    def store(self, kernel: SemanticKernel, auto_connect: bool = True) -> str:
        """
        Сохранить зерно в память

        Args:
            kernel: Семантическое зерно
            auto_connect: Автоматически связать с похожими зёрнами

        Returns:
            ID сохранённого зерна
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO kernels
            (id, essence, concepts, kernel_type, importance, timestamp,
             activation_count, last_accessed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kernel.id,
            kernel.essence,
            json.dumps(kernel.concepts),
            kernel.kernel_type.value,
            kernel.importance,
            kernel.timestamp.isoformat(),
            kernel.activation_count,
            kernel.last_accessed.isoformat() if kernel.last_accessed else None,
            json.dumps(kernel.metadata)
        ))

        conn.commit()
        conn.close()

        # Автоматически связать с похожими
        if auto_connect:
            self._auto_connect(kernel)

        return kernel.id

    def retrieve(self, kernel_id: str, activate: bool = True) -> Optional[SemanticKernel]:
        """
        Получить зерно по ID

        Args:
            kernel_id: ID зерна
            activate: Увеличить счётчик активаций

        Returns:
            SemanticKernel или None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, essence, concepts, kernel_type, importance, timestamp,
                   activation_count, last_accessed, metadata
            FROM kernels WHERE id = ?
        ''', (kernel_id,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # Восстановить зерно
        kernel = self._row_to_kernel(row)

        # Активировать
        if activate:
            kernel.activate()
            cursor.execute('''
                UPDATE kernels
                SET activation_count = ?, last_accessed = ?
                WHERE id = ?
            ''', (kernel.activation_count, kernel.last_accessed.isoformat(), kernel.id))
            conn.commit()

        conn.close()
        return kernel

    def search(
        self,
        query: str,
        limit: int = 10,
        min_importance: float = 0.3,
        kernel_types: Optional[List[KernelType]] = None
    ) -> List[Tuple[SemanticKernel, float]]:
        """
        Ассоциативный поиск зёрен по запросу

        Args:
            query: Поисковый запрос
            limit: Максимум результатов
            min_importance: Минимальная важность зёрен
            kernel_types: Фильтр по типам (опционально)

        Returns:
            Список (зерно, релевантность) отсортированный по релевантности
        """
        # Сжать запрос в зерно для извлечения концепций
        query_kernel = self.compressor.compress(query)

        # Получить все зёрна (фильтруя по важности и типу)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sql = 'SELECT * FROM kernels WHERE importance >= ?'
        params = [min_importance]

        if kernel_types:
            type_placeholders = ','.join('?' * len(kernel_types))
            sql += f' AND kernel_type IN ({type_placeholders})'
            params.extend([kt.value for kt in kernel_types])

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        # Вычислить релевантность для каждого зерна
        results = []
        for row in rows:
            kernel = self._row_to_kernel(row)
            relevance = self._calculate_relevance(query_kernel, kernel)
            results.append((kernel, relevance))

        # Отсортировать по релевантности
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def find_similar(
        self,
        kernel: SemanticKernel,
        limit: int = 5,
        min_similarity: float = 0.3
    ) -> List[Tuple[SemanticKernel, float]]:
        """
        Найти похожие зёрна

        Args:
            kernel: Исходное зерно
            limit: Максимум результатов
            min_similarity: Минимальное сходство

        Returns:
            Список (зерно, сходство)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Получить все зёрна кроме себя
        cursor.execute('SELECT * FROM kernels WHERE id != ?', (kernel.id,))
        rows = cursor.fetchall()
        conn.close()

        # Вычислить сходство
        results = []
        for row in rows:
            other_kernel = self._row_to_kernel(row)
            similarity = self._calculate_similarity(kernel, other_kernel)

            if similarity >= min_similarity:
                results.append((other_kernel, similarity))

        # Отсортировать
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def connect(
        self,
        kernel_id1: str,
        kernel_id2: str,
        strength: float = 1.0,
        connection_type: str = "related"
    ):
        """
        Создать связь между двумя зёрнами

        Args:
            kernel_id1: ID первого зерна
            kernel_id2: ID второго зерна
            strength: Сила связи (0.0 - 1.0)
            connection_type: Тип связи (related, causes, depends_on, etc.)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO connections
            (kernel_id, connected_kernel_id, strength, connection_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            kernel_id1,
            kernel_id2,
            strength,
            connection_type,
            datetime.now().isoformat()
        ))

        # Создать обратную связь (граф неориентированный)
        cursor.execute('''
            INSERT OR REPLACE INTO connections
            (kernel_id, connected_kernel_id, strength, connection_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            kernel_id2,
            kernel_id1,
            strength,
            connection_type,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_connected(self, kernel_id: str, min_strength: float = 0.3) -> List[Tuple[SemanticKernel, float]]:
        """
        Получить все связанные зёрна

        Args:
            kernel_id: ID зерна
            min_strength: Минимальная сила связи

        Returns:
            Список (зерно, сила связи)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT k.*, c.strength
            FROM connections c
            JOIN kernels k ON c.connected_kernel_id = k.id
            WHERE c.kernel_id = ? AND c.strength >= ?
            ORDER BY c.strength DESC
        ''', (kernel_id, min_strength))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            kernel = self._row_to_kernel(row[:-1])  # Последнее поле - strength
            strength = row[-1]
            results.append((kernel, strength))

        return results

    def forget_unimportant(self, days_old: int = 30, importance_threshold: float = 0.3):
        """
        Забыть старые неважные зёрна (очистка памяти)

        Args:
            days_old: Удалить зёрна старше N дней
            importance_threshold: Удалить зёрна с важностью ниже порога
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Удалить старые неважные зёрна
        cursor.execute('''
            DELETE FROM kernels
            WHERE importance < ? AND timestamp < ?
        ''', (importance_threshold, cutoff_date.isoformat()))

        deleted_count = cursor.rowcount

        # Удалить связи с удалёнными зёрнами
        cursor.execute('''
            DELETE FROM connections
            WHERE kernel_id NOT IN (SELECT id FROM kernels)
               OR connected_kernel_id NOT IN (SELECT id FROM kernels)
        ''')

        conn.commit()
        conn.close()

        return deleted_count

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику памяти"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Всего зёрен
        cursor.execute('SELECT COUNT(*) FROM kernels')
        total_kernels = cursor.fetchone()[0]

        # Распределение по типам
        cursor.execute('''
            SELECT kernel_type, COUNT(*)
            FROM kernels
            GROUP BY kernel_type
        ''')
        type_distribution = dict(cursor.fetchall())

        # Средняя важность
        cursor.execute('SELECT AVG(importance) FROM kernels')
        avg_importance = cursor.fetchone()[0] or 0

        # Всего связей
        cursor.execute('SELECT COUNT(*) FROM connections')
        total_connections = cursor.fetchone()[0]

        # Топ активируемых зёрен
        cursor.execute('''
            SELECT id, essence, activation_count
            FROM kernels
            ORDER BY activation_count DESC
            LIMIT 5
        ''')
        top_activated = cursor.fetchall()

        conn.close()

        return {
            "total_kernels": total_kernels,
            "total_connections": total_connections,
            "type_distribution": type_distribution,
            "average_importance": avg_importance,
            "top_activated": [
                {"id": row[0], "essence": row[1], "activations": row[2]}
                for row in top_activated
            ]
        }

    def _auto_connect(self, kernel: SemanticKernel):
        """Автоматически связать зерно с похожими"""
        similar = self.find_similar(kernel, limit=5, min_similarity=0.5)

        for similar_kernel, similarity in similar:
            self.connect(
                kernel.id,
                similar_kernel.id,
                strength=similarity,
                connection_type="similar"
            )

    def _calculate_similarity(self, kernel1: SemanticKernel, kernel2: SemanticKernel) -> float:
        """
        Вычислить сходство между зёрнами

        Методы:
        1. Пересечение концепций (Жаккара)
        2. Схожесть типа
        3. Близость по важности
        """
        similarity = 0.0

        # 1. Пересечение концепций (вес 70%)
        concepts1 = set(kernel1.concepts)
        concepts2 = set(kernel2.concepts)

        if concepts1 or concepts2:
            intersection = len(concepts1 & concepts2)
            union = len(concepts1 | concepts2)
            jaccard = intersection / union if union > 0 else 0
            similarity += jaccard * 0.7

        # 2. Схожесть типа (вес 20%)
        if kernel1.kernel_type == kernel2.kernel_type:
            similarity += 0.2

        # 3. Близость важности (вес 10%)
        importance_diff = abs(kernel1.importance - kernel2.importance)
        importance_similarity = 1 - importance_diff
        similarity += importance_similarity * 0.1

        return min(similarity, 1.0)

    def _calculate_relevance(self, query_kernel: SemanticKernel, target_kernel: SemanticKernel) -> float:
        """
        Вычислить релевантность зерна к запросу

        Учитывает:
        1. Пересечение концепций
        2. Важность зерна
        3. Частоту использования
        """
        relevance = 0.0

        # 1. Пересечение концепций (вес 60%)
        query_concepts = set(query_kernel.concepts)
        target_concepts = set(target_kernel.concepts)

        if query_concepts:
            intersection = len(query_concepts & target_concepts)
            concept_score = intersection / len(query_concepts)
            relevance += concept_score * 0.6

        # 2. Важность (вес 30%)
        relevance += target_kernel.importance * 0.3

        # 3. Частота использования (вес 10%)
        # Нормализовать activation_count (логарифм для сглаживания)
        activation_score = min(math.log(target_kernel.activation_count + 1) / 5, 1.0)
        relevance += activation_score * 0.1

        return min(relevance, 1.0)

    def _row_to_kernel(self, row: Tuple) -> SemanticKernel:
        """Преобразовать строку БД в SemanticKernel"""
        return SemanticKernel(
            id=row[0],
            essence=row[1],
            concepts=json.loads(row[2]),
            kernel_type=KernelType(row[3]),
            importance=row[4],
            timestamp=datetime.fromisoformat(row[5]),
            activation_count=row[6],
            last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
            metadata=json.loads(row[8]) if row[8] else {}
        )


class KnowledgeGraph:
    """
    Граф знаний - визуализация связей между зёрнами

    Методы:
    - Обход графа
    - Поиск путей между зёрнами
    - Кластеризация похожих зёрен
    """

    def __init__(self, memory: SemanticMemory):
        self.memory = memory

    def find_path(
        self,
        start_kernel_id: str,
        end_kernel_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """
        Найти путь между двумя зёрнами (BFS)

        Args:
            start_kernel_id: Начальное зерно
            end_kernel_id: Конечное зерно
            max_depth: Максимальная глубина поиска

        Returns:
            Список ID зёрен в пути или None
        """
        if start_kernel_id == end_kernel_id:
            return [start_kernel_id]

        visited = set()
        queue = [(start_kernel_id, [start_kernel_id])]

        while queue:
            current_id, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            if current_id in visited:
                continue

            visited.add(current_id)

            # Получить связанные зёрна
            connected = self.memory.get_connected(current_id)

            for kernel, _ in connected:
                if kernel.id == end_kernel_id:
                    return path + [kernel.id]

                if kernel.id not in visited:
                    queue.append((kernel.id, path + [kernel.id]))

        return None

    def get_clusters(self, min_cluster_size: int = 3) -> List[List[SemanticKernel]]:
        """
        Найти кластеры похожих зёрен

        Args:
            min_cluster_size: Минимальный размер кластера

        Returns:
            Список кластеров (каждый кластер - список зёрен)
        """
        # Получить все зёрна
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM kernels')
        rows = cursor.fetchall()
        conn.close()

        kernels = [self.memory._row_to_kernel(row) for row in rows]

        # Простая кластеризация по типу и концепциям
        clusters_dict = defaultdict(list)

        for kernel in kernels:
            # Ключ кластера: тип + топ-2 концепции
            cluster_key = (
                kernel.kernel_type.value,
                tuple(sorted(kernel.concepts[:2]))
            )
            clusters_dict[cluster_key].append(kernel)

        # Отфильтровать маленькие кластеры
        clusters = [
            cluster for cluster in clusters_dict.values()
            if len(cluster) >= min_cluster_size
        ]

        return clusters


# Пример использования
if __name__ == "__main__":
    print("🧠 Semantic Memory - Смысловая память\n")

    # Создать память
    memory = SemanticMemory(db_path="test_memory.db")
    compressor = SemanticCompressor()

    # Пример 1: Сохранить зёрна
    print("Пример 1: Сохранение зёрен")

    messages = [
        "Пользователь хочет создать AI с мета-сознанием",
        "Решено использовать архитектуру из 5 слоёв",
        "Смысловая память сжимает контекст в 20-50 раз",
        "Нужен простой интуитивный интерфейс",
        "AI должен работать автономно 24/7"
    ]

    kernel_ids = []
    for msg in messages:
        kernel = compressor.compress(msg, language="ru")
        kernel_id = memory.store(kernel)
        kernel_ids.append(kernel_id)
        print(f"  ✅ Сохранено: {kernel.essence[:50]}...")

    # Пример 2: Поиск
    print("\nПример 2: Ассоциативный поиск")
    results = memory.search("автономная работа AI", limit=3)
    for kernel, relevance in results:
        print(f"  📌 [{relevance:.2f}] {kernel.essence}")

    # Пример 3: Похожие зёрна
    print("\nПример 3: Похожие зёрна")
    first_kernel = memory.retrieve(kernel_ids[0])
    similar = memory.find_similar(first_kernel, limit=3)
    for kernel, similarity in similar:
        print(f"  🔗 [{similarity:.2f}] {kernel.essence}")

    # Пример 4: Статистика
    print("\nПример 4: Статистика памяти")
    stats = memory.get_statistics()
    print(f"  Всего зёрен: {stats['total_kernels']}")
    print(f"  Всего связей: {stats['total_connections']}")
    print(f"  Средняя важность: {stats['average_importance']:.2f}")
    print(f"  Распределение по типам: {stats['type_distribution']}")

    # Пример 5: Граф знаний
    print("\nПример 5: Граф знаний")
    graph = KnowledgeGraph(memory)
    if len(kernel_ids) >= 2:
        path = graph.find_path(kernel_ids[0], kernel_ids[-1])
        if path:
            print(f"  Путь найден: {len(path)} шагов")
        else:
            print("  Путь не найден")

    print("\n✅ Смысловая память работает!")
