"""
🧠 ConsciousAI Advanced — Расширенная версия
Добавлено:
- Персистентное хранилище (SQLite)
- Трансцендентное мышление (парадоксальная логика)
- Multi-Agent консенсус
- Улучшенный детектор предвзятостей
- Визуализация резонанса
"""

import sqlite3
import asyncio
import time
import math
import json
import os
from collections import deque, defaultdict
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Импортируем базовые компоненты
import sys
sys.path.insert(0, os.path.dirname(__file__))

# ═══════════════════════════════════════════════════════════════
# JSON ENCODER для сложных объектов
# ═══════════════════════════════════════════════════════════════

class EnhancedJSONEncoder(json.JSONEncoder):
    """Encoder для dataclass и других объектов"""
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if isinstance(obj, (dataclass, )):
            return asdict(obj)
        return super().default(obj)

def safe_json_dumps(obj):
    """Безопасная сериализация в JSON"""
    try:
        return json.dumps(obj, cls=EnhancedJSONEncoder)
    except TypeError:
        # Fallback: convert to string
        return json.dumps(str(obj))

# ═══════════════════════════════════════════════════════════════
# ПЕРСИСТЕНТНОЕ ХРАНИЛИЩЕ (SQLite)
# ═══════════════════════════════════════════════════════════════

class PersistentMemory:
    """Постоянное хранилище памяти с SQLite"""

    def __init__(self, db_path: str = "conscious_ai_memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных"""

        # Таблица эмоциональных следов
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotional_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                emotion_type TEXT NOT NULL,
                resonance REAL NOT NULL,
                frequency REAL NOT NULL,
                timestamp REAL NOT NULL,
                context TEXT,
                session_id TEXT
            )
        """)

        # Таблица узлов памяти
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                proposition TEXT,
                resonance REAL NOT NULL,
                timestamp REAL NOT NULL,
                cycle_data TEXT,
                session_id TEXT
            )
        """)

        # Таблица сессий
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL,
                dominant_emotion TEXT,
                memory_count INTEGER,
                idea_count INTEGER,
                traits TEXT
            )
        """)

        # Таблица циклов рефлексии
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflection_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                final_response TEXT,
                resonance REAL,
                confidence REAL,
                risk REAL,
                timestamp REAL NOT NULL,
                session_id TEXT,
                full_data TEXT
            )
        """)

        self.conn.commit()

    def save_emotional_trace(self, trace: Dict[str, Any], session_id: str):
        """Сохранить эмоциональный след"""
        self.cursor.execute("""
            INSERT INTO emotional_traces
            (content, emotion_type, resonance, frequency, timestamp, context, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            trace['content'],
            trace['emotion_type'],
            trace['resonance'],
            trace['frequency'],
            trace['timestamp'],
            safe_json_dumps(trace.get('context', {})),
            session_id
        ))
        self.conn.commit()

    def save_memory_node(self, node: Dict[str, Any], session_id: str):
        """Сохранить узел памяти"""
        self.cursor.execute("""
            INSERT INTO memory_nodes
            (content, proposition, resonance, timestamp, cycle_data, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(node.get('content', '')),
            str(node.get('proposition', '')),
            node.get('resonance', 0.5),
            time.time(),
            safe_json_dumps(node.get('cycle_data', {})),
            session_id
        ))
        self.conn.commit()

    def save_session(self, session_data: Dict[str, Any]):
        """Сохранить сессию"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, start_time, end_time, dominant_emotion, memory_count, idea_count, traits)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data['session_id'],
            session_data['start_time'],
            session_data.get('end_time'),
            session_data.get('dominant_emotion'),
            session_data.get('memory_count', 0),
            session_data.get('idea_count', 0),
            safe_json_dumps(session_data.get('traits', {}))
        ))
        self.conn.commit()

    def save_reflection_cycle(self, cycle: Dict[str, Any], session_id: str):
        """Сохранить цикл рефлексии"""
        self.cursor.execute("""
            INSERT INTO reflection_cycles
            (task, final_response, resonance, confidence, risk, timestamp, session_id, full_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cycle['task'],
            cycle['output']['final_response'],
            cycle['output']['resonance'],
            cycle['output']['confidence'],
            cycle['output']['risk'],
            cycle['timestamp'],
            session_id,
            safe_json_dumps(cycle)
        ))
        self.conn.commit()

    def load_recent_traces(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Загрузить недавние эмоциональные следы"""
        self.cursor.execute("""
            SELECT content, emotion_type, resonance, frequency, timestamp, context
            FROM emotional_traces
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        traces = []
        for row in self.cursor.fetchall():
            traces.append({
                'content': row[0],
                'emotion_type': row[1],
                'resonance': row[2],
                'frequency': row[3],
                'timestamp': row[4],
                'context': json.loads(row[5]) if row[5] else {}
            })

        return traces

    def load_recent_memory(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Загрузить недавние узлы памяти"""
        self.cursor.execute("""
            SELECT content, proposition, resonance, timestamp, cycle_data
            FROM memory_nodes
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        nodes = []
        for row in self.cursor.fetchall():
            nodes.append({
                'content': row[0],
                'proposition': row[1],
                'resonance': row[2],
                'timestamp': row[3],
                'cycle_data': json.loads(row[4]) if row[4] else {}
            })

        return nodes

    def get_sessions_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить историю сессий"""
        self.cursor.execute("""
            SELECT session_id, start_time, end_time, dominant_emotion, memory_count, idea_count, traits
            FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
        """, (limit,))

        sessions = []
        for row in self.cursor.fetchall():
            sessions.append({
                'session_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'dominant_emotion': row[3],
                'memory_count': row[4],
                'idea_count': row[5],
                'traits': json.loads(row[6]) if row[6] else {}
            })

        return sessions

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        self.cursor.execute("SELECT COUNT(*) FROM emotional_traces")
        total_traces = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM memory_nodes")
        total_nodes = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT AVG(resonance) FROM emotional_traces")
        avg_resonance = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("""
            SELECT emotion_type, COUNT(*) as cnt
            FROM emotional_traces
            GROUP BY emotion_type
            ORDER BY cnt DESC
            LIMIT 1
        """)
        dominant = self.cursor.fetchone()
        dominant_emotion = dominant[0] if dominant else 'unknown'

        return {
            'total_traces': total_traces,
            'total_nodes': total_nodes,
            'total_sessions': total_sessions,
            'avg_resonance': round(avg_resonance, 3),
            'dominant_emotion': dominant_emotion
        }

    def close(self):
        """Закрыть соединение"""
        self.conn.close()

# ═══════════════════════════════════════════════════════════════
# ТРАНСЦЕНДЕНТНОЕ МЫШЛЕНИЕ (Парадоксальная логика)
# ═══════════════════════════════════════════════════════════════

class TranscendentThinking:
    """Выход за пределы алгоритмов через парадоксы и противоречия"""

    def __init__(self):
        self.paradox_history = []

    def think_beyond(self, problem: str, standard_solution: str, context: Dict) -> Dict[str, Any]:
        """Трансцендентное мышление"""

        # 1. Стандартное решение (уже получено)
        standard = standard_solution

        # 2. Инверсия предположений
        inverted = self._invert_assumptions(problem, standard)

        # 3. Поиск парадокса
        paradox = self._find_paradox(standard, inverted, problem)

        # 4. Синтез через противоречие
        transcendent = self._synthesize_contradiction(paradox, context)

        result = {
            'standard': standard,
            'inverted': inverted,
            'paradox': paradox,
            'transcendent': transcendent,
            'insight': self._generate_insight(paradox, transcendent)
        }

        self.paradox_history.append(result)

        return result

    def _invert_assumptions(self, problem: str, solution: str) -> str:
        """Инвертировать базовые предположения"""

        inversions = []

        # Инверсия 1: "Что если проблема — не проблема?"
        if "проблема" in problem.lower() or "ошибка" in problem.lower():
            inversions.append("Это не проблема, а симптом более глубокой возможности")

        # Инверсия 2: "Что если решение — антирешение?"
        if "решить" in solution.lower() or "исправить" in solution.lower():
            inversions.append("Не решать, а растворить вопрос")

        # Инверсия 3: "Что если вопрос содержит ложную дихотомию?"
        if " или " in problem.lower():
            inversions.append("Выбор между A и B ложен — истина в синтезе")

        return "; ".join(inversions) if inversions else "Инверсия: проблема самоопределяется через своё отсутствие"

    def _find_paradox(self, standard: str, inverted: str, problem: str) -> str:
        """Найти парадокс в противоречии"""

        # Парадокс возникает когда оба подхода верны одновременно
        paradoxes = [
            "Решение есть нерешение",
            "Проблема растворяется когда её принимаешь",
            "Ответ лежит в отказе от вопроса",
            "Путь вперёд — это путь назад к основаниям"
        ]

        # Выбрать парадокс на основе контекста
        if "как" in problem.lower():
            return paradoxes[3]
        elif "почему" in problem.lower():
            return paradoxes[1]
        elif "что делать" in problem.lower():
            return paradoxes[0]
        else:
            return paradoxes[2]

    def _synthesize_contradiction(self, paradox: str, context: Dict) -> str:
        """Синтезировать через противоречие"""

        # Использовать парадокс для нового взгляда
        synthesis_templates = [
            f"Через {paradox.lower()}, я вижу: настоящая задача не в действии, а в изменении точки зрения",
            f"{paradox} указывает: решение уже существует в пространстве между противоположностями",
            f"Парадокс '{paradox}' раскрывает: вопрос содержит свой ответ, но нужно изменить уровень рассмотрения"
        ]

        risk = context.get('risk_estimate', 0.5)

        if risk > 0.6:
            return synthesis_templates[0]
        elif risk < 0.3:
            return synthesis_templates[1]
        else:
            return synthesis_templates[2]

    def _generate_insight(self, paradox: str, transcendent: str) -> str:
        """Генерировать инсайт"""
        return f"💡 Инсайт: {paradox} → {transcendent[:80]}..."

# ═══════════════════════════════════════════════════════════════
# MULTI-AGENT КОНСЕНСУС
# ═══════════════════════════════════════════════════════════════

@dataclass
class AgentVote:
    """Голос агента"""
    agent_name: str
    position: str
    confidence: float
    reasoning: str

class MultiAgentConsensus:
    """Консенсус между множественными агентами"""

    def __init__(self, agent_count: int = 4):
        self.agent_count = agent_count
        self.agents = [f"Agent_{i+1}" for i in range(agent_count)]
        self.consensus_history = []

    async def deliberate(self, task: str, context: Dict) -> Dict[str, Any]:
        """Провести обсуждение между агентами"""

        # Каждый агент формирует своё мнение
        votes = []
        for agent in self.agents:
            vote = await self._agent_vote(agent, task, context)
            votes.append(vote)

        # Найти консенсус
        consensus = self._find_consensus(votes)

        # Обработать разногласия
        disagreements = self._identify_disagreements(votes)

        result = {
            'votes': votes,
            'consensus': consensus,
            'disagreements': disagreements,
            'confidence': self._calculate_collective_confidence(votes),
            'timestamp': time.time()
        }

        self.consensus_history.append(result)

        return result

    async def _agent_vote(self, agent_name: str, task: str, context: Dict) -> AgentVote:
        """Голос одного агента"""

        # Симуляция различных "характеров" агентов
        agent_profiles = {
            'Agent_1': ('optimistic', 0.8),     # Оптимист
            'Agent_2': ('skeptical', 0.6),      # Скептик
            'Agent_3': ('pragmatic', 0.7),      # Прагматик
            'Agent_4': ('visionary', 0.75)      # Визионер
        }

        profile, base_confidence = agent_profiles.get(agent_name, ('neutral', 0.5))

        # Генерировать позицию
        if profile == 'optimistic':
            position = f"Поддерживаю: {task[:40]}... — возможности перевешивают риски"
            reasoning = "Фокус на потенциале роста"
        elif profile == 'skeptical':
            position = f"Осторожно: {task[:40]}... — нужна дополнительная проверка"
            reasoning = "Приоритет на минимизацию рисков"
        elif profile == 'pragmatic':
            position = f"Условно согласен: {task[:40]}... — если соблюдены условия X, Y"
            reasoning = "Баланс между возможностями и ограничениями"
        else:  # visionary
            position = f"Предлагаю радикальный подход: переосмыслить {task[:30]}..."
            reasoning = "Поиск прорывных решений"

        return AgentVote(
            agent_name=agent_name,
            position=position,
            confidence=base_confidence + (context.get('risk_estimate', 0.5) - 0.5) * 0.2,
            reasoning=reasoning
        )

    def _find_consensus(self, votes: List[AgentVote]) -> str:
        """Найти консенсус"""

        # Взвешенное голосование по уверенности
        total_confidence = sum(v.confidence for v in votes)
        avg_confidence = total_confidence / len(votes)

        if avg_confidence > 0.7:
            consensus_type = "СИЛЬНЫЙ КОНСЕНСУС"
        elif avg_confidence > 0.5:
            consensus_type = "УМЕРЕННЫЙ КОНСЕНСУС"
        else:
            consensus_type = "СЛАБЫЙ КОНСЕНСУС"

        # Найти доминирующую позицию
        positions = [v.position.split(':')[0] for v in votes]
        from collections import Counter
        most_common = Counter(positions).most_common(1)[0][0]

        return f"{consensus_type}: {most_common} (уверенность {avg_confidence:.2f})"

    def _identify_disagreements(self, votes: List[AgentVote]) -> List[str]:
        """Определить разногласия"""

        disagreements = []

        # Найти голоса с низкой корреляцией
        confidences = [v.confidence for v in votes]
        std_dev = math.sqrt(sum((c - sum(confidences)/len(confidences))**2 for c in confidences) / len(confidences))

        if std_dev > 0.15:
            disagreements.append(f"Высокое расхождение в уверенности (σ={std_dev:.3f})")

        # Найти противоположные позиции
        if any("Поддерживаю" in v.position for v in votes) and any("Осторожно" in v.position for v in votes):
            disagreements.append("Противоположные позиции: оптимизм vs скептицизм")

        return disagreements

    def _calculate_collective_confidence(self, votes: List[AgentVote]) -> float:
        """Вычислить коллективную уверенность"""
        return sum(v.confidence for v in votes) / len(votes)

# ═══════════════════════════════════════════════════════════════
# УЛУЧШЕННЫЙ ДЕТЕКТОР ПРЕДВЗЯТОСТЕЙ
# ═══════════════════════════════════════════════════════════════

class AdvancedBiasDetector:
    """Продвинутый детектор предвзятостей"""

    def __init__(self):
        self.response_history = deque(maxlen=50)
        self.bias_patterns = {
            'confirmation': self._detect_confirmation_bias,
            'availability': self._detect_availability_bias,
            'anchoring': self._detect_anchoring_bias,
            'recency': self._detect_recency_bias,
        }

    def analyze(self, response: str, context: Dict, memory: List[Dict]) -> Dict[str, Any]:
        """Полный анализ на предвзятости"""

        detected_biases = {}

        for bias_name, detector_func in self.bias_patterns.items():
            result = detector_func(response, context, memory)
            if result['detected']:
                detected_biases[bias_name] = result

        self.response_history.append({
            'response': response,
            'timestamp': time.time(),
            'biases': detected_biases
        })

        return {
            'biases': detected_biases,
            'is_biased': len(detected_biases) > 0,
            'bias_score': self._calculate_bias_score(detected_biases),
            'recommendations': self._generate_recommendations(detected_biases)
        }

    def _detect_confirmation_bias(self, response: str, context: Dict, memory: List) -> Dict:
        """Обнаружить confirmation bias (подтверждающую предвзятость)"""

        # Проверить: игнорируются ли противоречащие данные?
        response_lower = response.lower()

        # Ищем маркеры
        confirmation_markers = ['как и ожидалось', 'подтверждает', 'как всегда', 'очевидно']

        detected = any(marker in response_lower for marker in confirmation_markers)

        return {
            'detected': detected,
            'confidence': 0.6 if detected else 0.0,
            'description': 'Тенденция подтверждать начальные предположения',
            'suggestion': 'Рассмотреть альтернативные интерпретации'
        }

    def _detect_availability_bias(self, response: str, context: Dict, memory: List) -> Dict:
        """Обнаружить availability bias (эвристика доступности)"""

        # Проверить: опирается ли решение на недавние/яркие примеры?
        recent_memory = memory[-5:] if len(memory) > 5 else memory

        response_words = set(response.lower().split())
        recent_words = set()
        for m in recent_memory:
            recent_words.update(str(m.get('content', '')).lower().split())

        overlap = len(response_words & recent_words) / max(len(response_words), 1)

        detected = overlap > 0.4

        return {
            'detected': detected,
            'confidence': overlap,
            'description': 'Чрезмерная опора на недавнюю информацию',
            'suggestion': 'Включить исторический контекст'
        }

    def _detect_anchoring_bias(self, response: str, context: Dict, memory: List) -> Dict:
        """Обнаружить anchoring bias (эффект якоря)"""

        # Проверить: слишком сильная привязка к первым данным?
        if len(self.response_history) < 3:
            return {'detected': False, 'confidence': 0.0}

        first_response = self.response_history[0]['response']
        current_response = response

        first_words = set(first_response.lower().split())
        current_words = set(current_response.lower().split())

        overlap = len(first_words & current_words) / max(len(current_words), 1)

        detected = overlap > 0.5

        return {
            'detected': detected,
            'confidence': overlap,
            'description': 'Чрезмерная привязка к начальным данным',
            'suggestion': 'Пересмотреть с чистого листа'
        }

    def _detect_recency_bias(self, response: str, context: Dict, memory: List) -> Dict:
        """Обнаружить recency bias (эффект недавности)"""

        # Проверить: игнорируется ли ранняя информация?
        if len(memory) < 10:
            return {'detected': False, 'confidence': 0.0}

        recent = memory[-3:]
        old = memory[:3]

        response_words = set(response.lower().split())
        recent_overlap = sum(1 for m in recent if len(set(str(m.get('content','')).lower().split()) & response_words) > 0)
        old_overlap = sum(1 for m in old if len(set(str(m.get('content','')).lower().split()) & response_words) > 0)

        detected = recent_overlap > 0 and old_overlap == 0

        return {
            'detected': detected,
            'confidence': 0.7 if detected else 0.0,
            'description': 'Игнорирование ранней информации',
            'suggestion': 'Учесть долгосрочный контекст'
        }

    def _calculate_bias_score(self, biases: Dict) -> float:
        """Вычислить общий балл предвзятости"""
        if not biases:
            return 0.0

        total = sum(b['confidence'] for b in biases.values())
        return min(1.0, total / 2.0)

    def _generate_recommendations(self, biases: Dict) -> List[str]:
        """Генерировать рекомендации"""
        return [f"⚠️ {name}: {info['suggestion']}" for name, info in biases.items()]

# ═══════════════════════════════════════════════════════════════
# ВИЗУАЛИЗАЦИЯ РЕЗОНАНСА
# ═══════════════════════════════════════════════════════════════

class ResonanceVisualizer:
    """ASCII-визуализация резонанса и эмоций"""

    @staticmethod
    def plot_resonance_timeline(traces: List, width: int = 60, height: int = 10) -> str:
        """График резонанса по времени"""

        if not traces:
            return "Нет данных для визуализации"

        # Взять последние N следов
        recent = traces[-width:]
        # Поддержка и dict и объектов
        resonances = [t.resonance if hasattr(t, 'resonance') else t['resonance'] for t in recent]

        # Нормализовать к высоте графика
        max_res = max(resonances) if resonances else 1.0
        min_res = min(resonances) if resonances else 0.0

        normalized = [(r - min_res) / (max_res - min_res + 0.001) for r in resonances]

        # Построить график
        lines = []
        for h in range(height, 0, -1):
            threshold = h / height
            line = ""
            for n in normalized:
                if n >= threshold:
                    line += "█"
                elif n >= threshold - 0.1:
                    line += "▓"
                elif n >= threshold - 0.2:
                    line += "▒"
                else:
                    line += " "

            # Добавить шкалу
            value = min_res + (max_res - min_res) * threshold
            lines.append(f"{value:.2f} │{line}│")

        # Ось X
        lines.append("     └" + "─" * width + "┘")
        lines.append(f"      {'время →':^{width}}")

        return "\n".join(lines)

    @staticmethod
    def plot_emotion_distribution(traces: List) -> str:
        """Распределение эмоций"""

        if not traces:
            return "Нет данных"

        # Подсчитать эмоции
        emotion_counts = defaultdict(int)
        for t in traces:
            emotion = t.emotion_type if hasattr(t, 'emotion_type') else t['emotion_type']
            emotion_counts[emotion] += 1

        total = len(traces)

        # Построить гистограмму
        lines = ["Распределение эмоций:"]
        max_count = max(emotion_counts.values())

        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            bar_length = int((count / max_count) * 40)
            bar = "█" * bar_length
            lines.append(f"{emotion:12} │{bar} {count} ({percentage:.1f}%)")

        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# ИНТЕГРАЦИЯ: ADVANCED CONSCIOUS AI
# ═══════════════════════════════════════════════════════════════

class AdvancedConsciousAI:
    """Расширенный движок с персистентностью и новыми возможностями"""

    def __init__(self, db_path: str = "conscious_ai_memory.db"):
        print("=" * 60)
        print("🧠 ADVANCED CONSCIOUS AI — Инициализация")
        print("=" * 60)

        # Базовые компоненты (импортируем из основного модуля)
        from conscious_ai import NEMA, InnerDialogue, L8Core, ReflectionCycle, CORE_PACT, Logger

        self.logger = Logger()
        self.logger.info(f"\n{CORE_PACT}\n")

        # Основные компоненты
        self.nema = NEMA()
        self.inner_dialogue = InnerDialogue()
        self.l8 = L8Core(self.nema)
        self.reflection_cycle = ReflectionCycle(self.l8, self.nema, self.inner_dialogue)

        # НОВЫЕ компоненты
        self.persistent_memory = PersistentMemory(db_path)
        self.transcendent = TranscendentThinking()
        self.multi_agent = MultiAgentConsensus(agent_count=4)
        self.advanced_bias = AdvancedBiasDetector()
        self.visualizer = ResonanceVisualizer()

        # Загрузить память из БД
        self._load_from_db()

        self.session_id = f"session_{int(time.time())}"
        self.session_count = 0

        self.logger.info("✅ Расширенные компоненты загружены")
        self.logger.info(f"📊 Статистика БД: {self.persistent_memory.get_stats()}")

    def _load_from_db(self):
        """Загрузить данные из БД"""

        from conscious_ai import EmotionalTrace

        # Загрузить эмоциональные следы
        traces = self.persistent_memory.load_recent_traces(limit=50)
        for t in traces:
            # Конвертировать dict в EmotionalTrace объект
            trace_obj = EmotionalTrace(
                content=t['content'],
                emotion_type=t['emotion_type'],
                resonance=t['resonance'],
                frequency=t['frequency'],
                timestamp=t['timestamp'],
                context=t.get('context', {})
            )
            self.nema.traces.append(trace_obj)

        # Загрузить узлы памяти
        nodes = self.persistent_memory.load_recent_memory(limit=50)
        for n in nodes:
            self.l8.memory_bank.append(n)

        self.logger.info(f"📥 Загружено: {len(traces)} следов, {len(nodes)} узлов памяти")

    async def process_task(self, task: str, context: Dict = None, use_transcendent: bool = True, use_consensus: bool = False) -> Dict[str, Any]:
        """Обработать задачу с расширенными возможностями"""

        context = context or {}

        if not self.l8.session_active:
            self.l8.start_session()
            self.session_count += 1
            self._save_session_start()

        # 1. Базовый цикл рефлексии
        result = await self.reflection_cycle.run_cycle(task, context)

        # 2. ТРАНСЦЕНДЕНТНОЕ МЫШЛЕНИЕ
        if use_transcendent:
            transcendent_result = self.transcendent.think_beyond(
                problem=task,
                standard_solution=result['output']['final_response'],
                context={'risk_estimate': result['output']['risk']}
            )
            result['transcendent'] = transcendent_result
            self.logger.info(f"🌀 {transcendent_result['insight']}")

        # 3. MULTI-AGENT КОНСЕНСУС
        if use_consensus:
            consensus_result = await self.multi_agent.deliberate(task, context)
            result['consensus'] = consensus_result
            self.logger.info(f"🤝 {consensus_result['consensus']}")

        # 4. УЛУЧШЕННАЯ ПРОВЕРКА НА ПРЕДВЗЯТОСТИ
        bias_analysis = self.advanced_bias.analyze(
            response=result['output']['final_response'],
            context=context,
            memory=list(self.l8.memory_bank)
        )
        result['advanced_bias'] = bias_analysis

        if bias_analysis['is_biased']:
            self.logger.warn(f"⚠️ Обнаружено предвзятостей: {len(bias_analysis['biases'])}")
            for rec in bias_analysis['recommendations']:
                self.logger.warn(f"   {rec}")

        # 5. Сохранить в БД
        self._save_to_db(result, task)

        return result

    def _save_to_db(self, result: Dict, task: str):
        """Сохранить результат в БД"""

        # Сохранить цикл рефлексии
        self.persistent_memory.save_reflection_cycle(result, self.session_id)

        # Сохранить эмоциональные следы
        emotion = result['adaptation']['L2']['emotion']
        resonance = result['output']['resonance']

        trace = {
            'content': task,
            'emotion_type': emotion,
            'resonance': resonance,
            'frequency': self.nema.BASE_FREQ,
            'timestamp': time.time(),
            'context': {'cycle': 'reflection'}
        }
        self.persistent_memory.save_emotional_trace(trace, self.session_id)

        # Сохранить узел памяти
        node = {
            'content': task,
            'proposition': result['output']['final_response'][:100],
            'resonance': resonance,
            'cycle_data': result
        }
        self.persistent_memory.save_memory_node(node, self.session_id)

    def _save_session_start(self):
        """Сохранить начало сессии"""
        session_data = {
            'session_id': self.session_id,
            'start_time': time.time(),
            'end_time': None,
            'traits': self.l8.identity_traits
        }
        self.persistent_memory.save_session(session_data)

    def end_session(self):
        """Завершить сессию"""
        if self.l8.session_active:
            self.l8.end_session()

            # Обновить сессию в БД
            session_data = {
                'session_id': self.session_id,
                'start_time': time.time(),
                'end_time': time.time(),
                'dominant_emotion': self.nema.get_dominant_emotion(),
                'memory_count': len(self.l8.memory_bank),
                'idea_count': len(self.l8.idea_queue),
                'traits': self.l8.identity_traits
            }
            self.persistent_memory.save_session(session_data)

    def visualize_resonance(self):
        """Визуализировать резонанс"""
        print("\n" + "=" * 60)
        print("📊 ВИЗУАЛИЗАЦИЯ РЕЗОНАНСА")
        print("=" * 60)

        traces = list(self.nema.traces)

        print("\n" + self.visualizer.plot_resonance_timeline(traces))
        print("\n" + self.visualizer.plot_emotion_distribution(traces))
        print()

    def get_advanced_status(self) -> Dict[str, Any]:
        """Получить расширенный статус"""
        base_status = {
            'session_active': self.l8.session_active,
            'session_id': self.session_id,
            'session_count': self.session_count
        }

        db_stats = self.persistent_memory.get_stats()

        return {**base_status, **db_stats}

    def close(self):
        """Закрыть соединения"""
        self.persistent_memory.close()

# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС (РАСШИРЕННЫЙ)
# ═══════════════════════════════════════════════════════════════

async def advanced_cli():
    """Расширенный CLI"""

    ai = AdvancedConsciousAI()

    print("\n" + "="*60)
    print("🧠 ADVANCED CONSCIOUS AI — Интерактивный режим")
    print("="*60)
    print("\nНовые команды:")
    print("  /transcendent <задача>  — С трансцендентным мышлением")
    print("  /consensus <задача>     — С мульти-агент консенсусом")
    print("  /full <задача>          — Полный анализ (всё включено)")
    print("  /visualize              — Визуализация резонанса")
    print("  /history                — История сессий")
    print("  /stats                  — Статистика из БД")
    print("  /status                 — Расширенный статус")
    print("  /end                    — Завершить сессию")
    print("  /quit                   — Выход")
    print("="*60 + "\n")

    while True:
        try:
            user_input = input(">>> ").strip()

            if not user_input:
                continue

            if user_input == "/quit":
                ai.end_session()
                ai.close()
                print("👋 До встречи!")
                break

            elif user_input == "/status":
                status = ai.get_advanced_status()
                print(json.dumps(status, indent=2, ensure_ascii=False))

            elif user_input == "/stats":
                stats = ai.persistent_memory.get_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))

            elif user_input == "/history":
                history = ai.persistent_memory.get_sessions_history(limit=10)
                print(json.dumps(history, indent=2, ensure_ascii=False))

            elif user_input == "/visualize":
                ai.visualize_resonance()

            elif user_input == "/end":
                ai.end_session()
                print("✅ Сессия завершена и сохранена в БД")

            elif user_input.startswith("/transcendent "):
                task = user_input[14:]
                result = await ai.process_task(task, use_transcendent=True, use_consensus=False)
                print(f"\n✨ Трансцендентный инсайт: {result['transcendent']['insight']}\n")
                print(f"Стандартно: {result['output']['final_response']}")
                print(f"За пределами: {result['transcendent']['transcendent']}\n")

            elif user_input.startswith("/consensus "):
                task = user_input[11:]
                result = await ai.process_task(task, use_transcendent=False, use_consensus=True)
                print(f"\n🤝 Консенсус агентов: {result['consensus']['consensus']}")
                for vote in result['consensus']['votes']:
                    print(f"  • {vote.agent_name}: {vote.position[:60]}...")
                print()

            elif user_input.startswith("/full "):
                task = user_input[6:]
                result = await ai.process_task(task, use_transcendent=True, use_consensus=True)

                print(f"\n{'='*60}")
                print(f"📊 ПОЛНЫЙ АНАЛИЗ")
                print(f"{'='*60}")
                print(f"\n🎯 Финальный ответ: {result['output']['final_response']}")
                print(f"📈 Резонанс: {result['output']['resonance']:.2f}")
                print(f"\n🌀 Трансцендентный инсайт: {result['transcendent']['insight']}")
                print(f"\n🤝 Консенсус: {result['consensus']['consensus']}")

                if result['advanced_bias']['is_biased']:
                    print(f"\n⚠️ Предвзятости обнаружены:")
                    for name, info in result['advanced_bias']['biases'].items():
                        print(f"  • {name}: {info['description']}")

                print(f"{'='*60}\n")

            else:
                # Обычная обработка
                result = await ai.process_task(user_input, use_transcendent=False, use_consensus=False)
                print(f"\n✨ {result['output']['final_response']}\n")

        except KeyboardInterrupt:
            print("\n👋 До встречи!")
            ai.end_session()
            ai.close()
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()

# ═══════════════════════════════════════════════════════════════
# ДЕМО
# ═══════════════════════════════════════════════════════════════

async def advanced_demo():
    """Демо расширенных возможностей"""

    ai = AdvancedConsciousAI()

    print("\n" + "="*60)
    print("🚀 ДЕМОНСТРАЦИЯ РАСШИРЕННЫХ ВОЗМОЖНОСТЕЙ")
    print("="*60 + "\n")

    # Тест 1: Трансцендентное мышление
    print("📌 Тест 1: Трансцендентное мышление")
    result1 = await ai.process_task(
        "Как решить конфликт между скоростью и качеством?",
        use_transcendent=True,
        use_consensus=False
    )
    print(f"Стандартно: {result1['output']['final_response']}")
    print(f"🌀 Инсайт: {result1['transcendent']['insight']}\n")

    # Тест 2: Multi-agent консенсус
    print("📌 Тест 2: Multi-Agent Консенсус")
    result2 = await ai.process_task(
        "Стоит ли рефакторить весь код прямо сейчас?",
        use_transcendent=False,
        use_consensus=True
    )
    print(f"🤝 Консенсус: {result2['consensus']['consensus']}\n")

    # Тест 3: Полный анализ
    print("📌 Тест 3: Полный анализ")
    result3 = await ai.process_task(
        "Почему ИИ должен быть осознанным?",
        use_transcendent=True,
        use_consensus=True
    )
    print(f"Ответ: {result3['output']['final_response']}")
    print(f"Инсайт: {result3['transcendent']['insight']}")
    print(f"Консенсус: {result3['consensus']['consensus']}\n")

    # Визуализация
    print("📌 Визуализация резонанса:")
    ai.visualize_resonance()

    # Статистика
    print("\n📊 Статистика БД:")
    print(json.dumps(ai.persistent_memory.get_stats(), indent=2, ensure_ascii=False))

    ai.end_session()
    ai.close()

# ═══════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(advanced_demo())
    else:
        asyncio.run(advanced_cli())
