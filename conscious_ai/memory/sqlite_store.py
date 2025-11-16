"""
ConsciousAI - SQLite реализация MemoryStore
Персистентное хранилище с SQL

Рекомендация GPT-5: Использовать абстракции для хранилища
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from .base import (
    BaseMemoryStore,
    SemanticKernel,
    SearchQuery,
    SearchResult,
    KernelType,
)
from ..utils import get_logger, MemoryStorageError, MemoryRetrievalError, handle_error

logger = get_logger(__name__)


class SQLiteMemoryStore(BaseMemoryStore):
    """
    SQLite реализация хранилища памяти

    Особенности:
    - Персистентность (данные сохраняются на диск)
    - Транзакции
    - Индексы для быстрого поиска
    - Connection pooling (в перспективе)
    """

    def __init__(self, db_path: str = "semantic_memory.db"):
        self.db_path = db_path
        logger.info(f"Инициализация SQLite store: {db_path}")
        self._init_database()

    def _init_database(self):
        """Создать таблицы и индексы"""
        try:
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
                    priority INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    activation_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    ttl INTEGER,
                    tags TEXT,
                    source TEXT DEFAULT 'user',
                    metadata TEXT
                )
            ''')

            # Таблица связей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connections (
                    kernel_id TEXT NOT NULL,
                    connected_id TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (kernel_id, connected_id),
                    FOREIGN KEY (kernel_id) REFERENCES kernels(id) ON DELETE CASCADE,
                    FOREIGN KEY (connected_id) REFERENCES kernels(id) ON DELETE CASCADE
                )
            ''')

            # Индексы для быстрого поиска
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON kernels(importance DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON kernels(timestamp DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON kernels(kernel_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON kernels(priority DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON kernels(source)')

            conn.commit()
            conn.close()
            logger.info("База данных инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise MemoryStorageError(f"Cannot initialize database: {e}")

    def _get_connection(self) -> sqlite3.Connection:
        """Получить соединение с БД"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            raise MemoryStorageError(f"Cannot connect to database: {e}")

    @handle_error
    def save(self, kernel: SemanticKernel) -> str:
        """Сохранить зерно в SQLite"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO kernels
                (id, essence, concepts, kernel_type, importance, priority,
                 timestamp, activation_count, last_accessed, ttl, tags, source, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                kernel.id,
                kernel.essence,
                json.dumps(kernel.concepts),
                kernel.kernel_type.value,
                kernel.importance,
                kernel.priority,
                kernel.timestamp.isoformat(),
                kernel.activation_count,
                kernel.last_accessed.isoformat() if kernel.last_accessed else None,
                kernel.ttl,
                json.dumps(kernel.tags),
                kernel.source,
                json.dumps(kernel.metadata)
            ))

            # Сохранить связи
            for connected_id in kernel.connections:
                cursor.execute('''
                    INSERT OR IGNORE INTO connections (kernel_id, connected_id, created_at)
                    VALUES (?, ?, ?)
                ''', (kernel.id, connected_id, datetime.now().isoformat()))

            conn.commit()
            logger.debug(f"Сохранено зерно: {kernel.id[:8]}...")
            return kernel.id

        finally:
            conn.close()

    @handle_error
    def get(self, kernel_id: str, activate: bool = True) -> Optional[SemanticKernel]:
        """Получить зерно по ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM kernels WHERE id = ?', (kernel_id,))
            row = cursor.fetchone()

            if not row:
                return None

            # Получить связи
            cursor.execute(
                'SELECT connected_id FROM connections WHERE kernel_id = ?',
                (kernel_id,)
            )
            connections = [r[0] for r in cursor.fetchall()]

            kernel = self._row_to_kernel(row, connections)

            # Активировать
            if activate:
                kernel.activate()
                cursor.execute('''
                    UPDATE kernels
                    SET activation_count = ?, last_accessed = ?
                    WHERE id = ?
                ''', (kernel.activation_count, kernel.last_accessed.isoformat(), kernel.id))
                conn.commit()

            return kernel

        finally:
            conn.close()

    @handle_error
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Поиск зёрен по запросу"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Построить SQL запрос
            sql = 'SELECT * FROM kernels WHERE 1=1'
            params = []

            # Фильтр по важности
            sql += ' AND importance >= ? AND importance <= ?'
            params.extend([query.min_importance, query.max_importance])

            # Фильтр по приоритету
            sql += ' AND priority >= ?'
            params.append(query.min_priority)

            # Фильтр по типу
            if query.kernel_types:
                placeholders = ','.join('?' * len(query.kernel_types))
                sql += f' AND kernel_type IN ({placeholders})'
                params.extend([kt.value for kt in query.kernel_types])

            # Фильтр по источнику
            if query.source:
                sql += ' AND source = ?'
                params.append(query.source)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Обработать результаты
            results = []
            for row in rows:
                # Получить связи
                cursor.execute(
                    'SELECT connected_id FROM connections WHERE kernel_id = ?',
                    (row[0],)
                )
                connections = [r[0] for r in cursor.fetchall()]
                kernel = self._row_to_kernel(row, connections)

                # Пропустить истёкшие
                if not query.include_expired and kernel.is_expired():
                    continue

                # Фильтр по тегам
                if query.tags:
                    if not set(query.tags).intersection(set(kernel.tags)):
                        continue

                # Вычислить релевантность
                score = self._calculate_score(query, kernel)

                if score > 0 or not query.text:  # Если нет текста, все релевантны
                    results.append(SearchResult(
                        kernel=kernel,
                        score=score,
                        match_reason=f"Relevance: {score:.2f}"
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

        finally:
            conn.close()

    def _calculate_score(self, query: SearchQuery, kernel: SemanticKernel) -> float:
        """Вычислить релевантность зерна к запросу"""
        score = 0.0

        # Совпадение текста в essence
        if query.text:
            text_lower = query.text.lower()
            essence_lower = kernel.essence.lower()

            # Точное совпадение
            if text_lower in essence_lower:
                score += 0.5

            # Слова из запроса
            query_words = set(text_lower.split())
            essence_words = set(essence_lower.split())
            word_overlap = len(query_words.intersection(essence_words))
            if query_words:
                score += (word_overlap / len(query_words)) * 0.2

            # Слова в концепциях
            kernel_concepts = set(c.lower() for c in kernel.concepts)
            concept_overlap = len(query_words.intersection(kernel_concepts))
            if query_words:
                score += (concept_overlap / len(query_words)) * 0.2

        # Совпадение концепций из запроса
        if query.concepts:
            query_concepts = set(c.lower() for c in query.concepts)
            kernel_concepts = set(c.lower() for c in kernel.concepts)
            overlap = len(query_concepts.intersection(kernel_concepts))
            if query_concepts:
                score += (overlap / len(query_concepts)) * 0.3

        # Бонус за важность
        score += kernel.importance * 0.1

        return min(score, 1.0)

    @handle_error
    def delete(self, kernel_id: str) -> bool:
        """Удалить зерно"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM kernels WHERE id = ?', (kernel_id,))
            deleted = cursor.rowcount > 0
            conn.commit()

            if deleted:
                logger.debug(f"Удалено зерно: {kernel_id[:8]}...")

            return deleted

        finally:
            conn.close()

    @handle_error
    def update(self, kernel: SemanticKernel) -> bool:
        """Обновить зерно"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE kernels SET
                    essence = ?,
                    concepts = ?,
                    kernel_type = ?,
                    importance = ?,
                    priority = ?,
                    activation_count = ?,
                    last_accessed = ?,
                    ttl = ?,
                    tags = ?,
                    source = ?,
                    metadata = ?
                WHERE id = ?
            ''', (
                kernel.essence,
                json.dumps(kernel.concepts),
                kernel.kernel_type.value,
                kernel.importance,
                kernel.priority,
                kernel.activation_count,
                kernel.last_accessed.isoformat() if kernel.last_accessed else None,
                kernel.ttl,
                json.dumps(kernel.tags),
                kernel.source,
                json.dumps(kernel.metadata),
                kernel.id
            ))

            updated = cursor.rowcount > 0
            conn.commit()
            return updated

        finally:
            conn.close()

    @handle_error
    def stats(self) -> Dict[str, Any]:
        """Получить статистику хранилища"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Всего зёрен
            cursor.execute('SELECT COUNT(*) FROM kernels')
            total_kernels = cursor.fetchone()[0]

            # По типам
            cursor.execute('SELECT kernel_type, COUNT(*) FROM kernels GROUP BY kernel_type')
            by_type = dict(cursor.fetchall())

            # Средняя важность
            cursor.execute('SELECT AVG(importance) FROM kernels')
            avg_importance = cursor.fetchone()[0] or 0

            # Всего связей
            cursor.execute('SELECT COUNT(*) FROM connections')
            total_connections = cursor.fetchone()[0]

            # Размер файла
            file_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0

            return {
                "total_kernels": total_kernels,
                "by_type": by_type,
                "avg_importance": avg_importance,
                "total_connections": total_connections // 2,
                "storage_size_bytes": file_size
            }

        finally:
            conn.close()

    @handle_error
    def cleanup(self, days_old: int = 30, importance_threshold: float = 0.2) -> int:
        """Очистить старые неважные зёрна"""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                DELETE FROM kernels
                WHERE importance < ? AND timestamp < ?
            ''', (importance_threshold, cutoff_date.isoformat()))

            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"Очищено {deleted_count} старых зёрен")
            return deleted_count

        finally:
            conn.close()

    def _row_to_kernel(self, row: tuple, connections: List[str] = None) -> SemanticKernel:
        """Преобразовать строку БД в SemanticKernel"""
        if connections is None:
            connections = []

        return SemanticKernel(
            id=row[0],
            essence=row[1],
            concepts=json.loads(row[2]),
            kernel_type=KernelType(row[3]),
            importance=row[4],
            priority=row[5],
            timestamp=datetime.fromisoformat(row[6]),
            activation_count=row[7],
            last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
            ttl=row[9],
            tags=json.loads(row[10]) if row[10] else [],
            source=row[11],
            metadata=json.loads(row[12]) if row[12] else {},
            connections=connections
        )


# Пример использования
if __name__ == "__main__":
    print("🗄️  Тест SQLite MemoryStore:\n")

    store = SQLiteMemoryStore(db_path="test_sqlite_store.db")

    # Сохранить зерно
    kernel = SemanticKernel(
        essence="SQLite хранилище работает!",
        concepts=["sqlite", "хранилище", "тест"],
        kernel_type=KernelType.FACT,
        importance=0.8,
        priority=5,
        tags=["test", "sqlite"]
    )

    kid = store.save(kernel)
    print(f"✅ Сохранено: {kid[:8]}...")

    # Получить
    retrieved = store.get(kid)
    print(f"✅ Получено: {retrieved.essence}")

    # Статистика
    stats = store.stats()
    print(f"\n📊 Статистика:")
    print(f"  Зёрен: {stats['total_kernels']}")
    print(f"  Размер БД: {stats['storage_size_bytes']} байт")

    print("\n✅ SQLite MemoryStore работает!")
