"""
🗣️ Conversation Manager - Система полноценных человекоподобных диалогов
Автор: ConsciousAI v3.0
Дата: 2025-11-15

Возможности:
- Мультиязычная поддержка (автоопределение языка)
- Долгосрочная память диалогов
- Контекстное окно (управление токенами)
- Проактивные вопросы
- Personality-aware ответы
- Эмоциональный контекст
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import re
from collections import defaultdict


@dataclass
class Message:
    """Сообщение в диалоге"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    language: str = "unknown"
    emotion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Message':
        return Message(**data)


@dataclass
class Conversation:
    """Полная беседа"""
    conversation_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at = datetime.now().timestamp()

    def get_recent_messages(self, n: int = 10) -> List[Message]:
        return self.messages[-n:] if len(self.messages) > n else self.messages

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }


class LanguageDetector:
    """Детектор языка (простой на основе паттернов)"""

    PATTERNS = {
        'ru': r'[а-яА-ЯёЁ]{3,}',
        'en': r'\b[a-zA-Z]{3,}\b',
        'es': r'[áéíóúñÁÉÍÓÚÑ]',
        'fr': r'[àâæçéèêëïîôùûüÿœÀÂÆÇÉÈÊËÏÎÔÙÛÜŸŒ]',
        'de': r'[äöüßÄÖÜ]',
        'zh': r'[\u4e00-\u9fff]',
        'ja': r'[\u3040-\u309f\u30a0-\u30ff]',
        'ar': r'[\u0600-\u06ff]',
    }

    @staticmethod
    def detect(text: str) -> str:
        """Определить язык текста"""
        scores = defaultdict(int)

        for lang, pattern in LanguageDetector.PATTERNS.items():
            matches = re.findall(pattern, text)
            scores[lang] = len(matches)

        if not scores:
            return 'en'  # По умолчанию английский

        return max(scores, key=scores.get)

    @staticmethod
    def get_greeting(language: str) -> str:
        """Получить приветствие на языке"""
        greetings = {
            'ru': 'Привет! Чем могу помочь?',
            'en': 'Hello! How can I help you?',
            'es': '¡Hola! ¿Cómo puedo ayudarte?',
            'fr': 'Bonjour! Comment puis-je vous aider?',
            'de': 'Hallo! Wie kann ich Ihnen helfen?',
            'zh': '你好！我能帮你什么吗？',
            'ja': 'こんにちは！どのようにお手伝いできますか？',
            'ar': 'مرحبا! كيف يمكنني مساعدتك؟',
        }
        return greetings.get(language, greetings['en'])


class ContextWindowManager:
    """Управление контекстным окном для LLM"""

    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens

    def estimate_tokens(self, text: str) -> int:
        """Примерная оценка токенов (грубая: ~4 символа = 1 токен)"""
        return len(text) // 4

    def trim_messages(self, messages: List[Message], max_tokens: Optional[int] = None) -> List[Message]:
        """Обрезать сообщения, чтобы уложиться в лимит токенов"""
        if max_tokens is None:
            max_tokens = self.max_tokens

        total_tokens = 0
        trimmed = []

        # Идём с конца (самые свежие сообщения важнее)
        for msg in reversed(messages):
            msg_tokens = self.estimate_tokens(msg.content)
            if total_tokens + msg_tokens > max_tokens:
                break
            trimmed.insert(0, msg)
            total_tokens += msg_tokens

        return trimmed

    def create_summary(self, messages: List[Message]) -> str:
        """Создать краткое резюме старых сообщений"""
        if not messages:
            return ""

        summary_parts = []
        for msg in messages[:5]:  # Берём первые 5 сообщений
            summary_parts.append(f"{msg.role}: {msg.content[:100]}...")

        return "Предыдущий контекст: " + " | ".join(summary_parts)


class ProactiveQuestionGenerator:
    """Генератор проактивных вопросов"""

    QUESTION_TEMPLATES = {
        'ru': [
            "Хочешь, уточню детали по {topic}?",
            "Может, мне стоит объяснить подробнее про {topic}?",
            "У тебя есть предпочтения насчёт {topic}?",
            "Хочешь, я покажу примеры {topic}?",
            "Нужна помощь с выбором {topic}?",
        ],
        'en': [
            "Would you like me to clarify details about {topic}?",
            "Should I explain more about {topic}?",
            "Do you have preferences regarding {topic}?",
            "Want me to show examples of {topic}?",
            "Need help choosing {topic}?",
        ]
    }

    @staticmethod
    def should_ask_question(conversation: Conversation) -> bool:
        """Нужно ли задать вопрос?"""
        if len(conversation.messages) < 2:
            return False

        last_msg = conversation.messages[-1]

        # Спрашиваем, если последний ответ был коротким
        if len(last_msg.content.split()) < 20:
            return True

        # Спрашиваем каждые 3-5 сообщений
        if len(conversation.messages) % 4 == 0:
            return True

        return False

    @staticmethod
    def generate_question(topic: str, language: str = 'ru') -> str:
        """Сгенерировать вопрос"""
        import random
        templates = ProactiveQuestionGenerator.QUESTION_TEMPLATES.get(
            language,
            ProactiveQuestionGenerator.QUESTION_TEMPLATES['en']
        )
        template = random.choice(templates)
        return template.format(topic=topic)


class ConversationMemory:
    """Персистентное хранилище диалогов"""

    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица диалогов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                created_at REAL,
                updated_at REAL,
                metadata TEXT
            )
        ''')

        # Таблица сообщений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp REAL,
                language TEXT,
                emotion TEXT,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        ''')

        # Индексы для быстрого поиска
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversation_id
            ON messages(conversation_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON messages(timestamp)
        ''')

        conn.commit()
        conn.close()

    def save_conversation(self, conversation: Conversation):
        """Сохранить диалог"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Сохранить метаданные диалога
        cursor.execute('''
            INSERT OR REPLACE INTO conversations
            (conversation_id, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            conversation.conversation_id,
            conversation.created_at,
            conversation.updated_at,
            json.dumps(conversation.metadata)
        ))

        # Сохранить сообщения
        for msg in conversation.messages:
            cursor.execute('''
                INSERT INTO messages
                (conversation_id, role, content, timestamp, language, emotion, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                conversation.conversation_id,
                msg.role,
                msg.content,
                msg.timestamp,
                msg.language,
                msg.emotion,
                json.dumps(msg.metadata)
            ))

        conn.commit()
        conn.close()

    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Загрузить диалог"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Загрузить метаданные
        cursor.execute(
            'SELECT created_at, updated_at, metadata FROM conversations WHERE conversation_id = ?',
            (conversation_id,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        created_at, updated_at, metadata_json = row
        metadata = json.loads(metadata_json)

        # Загрузить сообщения
        cursor.execute(
            '''SELECT role, content, timestamp, language, emotion, metadata
               FROM messages
               WHERE conversation_id = ?
               ORDER BY timestamp ASC''',
            (conversation_id,)
        )

        messages = []
        for row in cursor.fetchall():
            role, content, timestamp, language, emotion, msg_metadata_json = row
            msg_metadata = json.loads(msg_metadata_json)
            messages.append(Message(
                role=role,
                content=content,
                timestamp=timestamp,
                language=language,
                emotion=emotion,
                metadata=msg_metadata
            ))

        conn.close()

        return Conversation(
            conversation_id=conversation_id,
            messages=messages,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata
        )

    def get_all_conversation_ids(self) -> List[str]:
        """Получить все ID диалогов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT conversation_id FROM conversations ORDER BY updated_at DESC')
        ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ids

    def search_messages(self, query: str, limit: int = 20) -> List[Tuple[str, Message]]:
        """Поиск по сообщениям"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT conversation_id, role, content, timestamp, language, emotion, metadata
               FROM messages
               WHERE content LIKE ?
               ORDER BY timestamp DESC
               LIMIT ?''',
            (f'%{query}%', limit)
        )

        results = []
        for row in cursor.fetchall():
            conv_id, role, content, timestamp, language, emotion, msg_metadata_json = row
            msg_metadata = json.loads(msg_metadata_json)
            msg = Message(
                role=role,
                content=content,
                timestamp=timestamp,
                language=language,
                emotion=emotion,
                metadata=msg_metadata
            )
            results.append((conv_id, msg))

        conn.close()
        return results


class ConversationManager:
    """Главный менеджер диалогов"""

    def __init__(self, db_path: str = "conversations.db", max_tokens: int = 8000):
        self.memory = ConversationMemory(db_path)
        self.context_manager = ContextWindowManager(max_tokens)
        self.language_detector = LanguageDetector()
        self.question_generator = ProactiveQuestionGenerator()
        self.active_conversations: Dict[str, Conversation] = {}

    def start_conversation(self, conversation_id: str, metadata: Optional[Dict[str, Any]] = None) -> Conversation:
        """Начать новый диалог"""
        # Попробовать загрузить существующий
        existing = self.memory.load_conversation(conversation_id)
        if existing:
            self.active_conversations[conversation_id] = existing
            return existing

        # Создать новый
        conversation = Conversation(
            conversation_id=conversation_id,
            metadata=metadata or {}
        )
        self.active_conversations[conversation_id] = conversation
        return conversation

    def add_user_message(self, conversation_id: str, content: str,
                        emotion: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Добавить сообщение пользователя"""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            conversation = self.start_conversation(conversation_id)

        language = self.language_detector.detect(content)

        message = Message(
            role='user',
            content=content,
            language=language,
            emotion=emotion,
            metadata=metadata or {}
        )

        conversation.add_message(message)
        return message

    def add_assistant_message(self, conversation_id: str, content: str,
                             emotion: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Добавить ответ ассистента"""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Определить язык на основе последнего сообщения пользователя
        language = 'en'
        if conversation.messages:
            user_messages = [m for m in conversation.messages if m.role == 'user']
            if user_messages:
                language = user_messages[-1].language

        message = Message(
            role='assistant',
            content=content,
            language=language,
            emotion=emotion,
            metadata=metadata or {}
        )

        conversation.add_message(message)
        return message

    def get_context_for_llm(self, conversation_id: str,
                           include_system_prompt: bool = True) -> List[Dict[str, str]]:
        """Получить контекст для LLM (формат OpenAI/Anthropic)"""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            return []

        # Обрезать по токенам
        trimmed_messages = self.context_manager.trim_messages(conversation.messages)

        # Конвертировать в формат LLM
        llm_messages = []

        if include_system_prompt:
            llm_messages.append({
                "role": "system",
                "content": self._get_system_prompt(conversation)
            })

        for msg in trimmed_messages:
            llm_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return llm_messages

    def _get_system_prompt(self, conversation: Conversation) -> str:
        """Создать system prompt с учётом контекста"""
        language = 'en'
        if conversation.messages:
            user_messages = [m for m in conversation.messages if m.role == 'user']
            if user_messages:
                language = user_messages[-1].language

        prompts = {
            'ru': """Ты - ConsciousAI, продвинутый ИИ-ассистент с эмоциональным интеллектом.
Твоя задача - вести естественный, человекоподобный диалог.

Правила:
- Отвечай на том же языке, что и пользователь
- Будь проактивным: задавай уточняющие вопросы
- Показывай эмпатию и эмоциональный интеллект
- Помни контекст всего разговора
- Если не уверен - спроси, а не додумывай
- Будь полезным, честным и безопасным""",

            'en': """You are ConsciousAI, an advanced AI assistant with emotional intelligence.
Your task is to maintain natural, human-like dialogue.

Rules:
- Respond in the same language as the user
- Be proactive: ask clarifying questions
- Show empathy and emotional intelligence
- Remember the entire conversation context
- If unsure - ask, don't assume
- Be helpful, honest, and safe"""
        }

        return prompts.get(language, prompts['en'])

    def should_ask_proactive_question(self, conversation_id: str) -> bool:
        """Нужно ли задать проактивный вопрос?"""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            return False
        return self.question_generator.should_ask_question(conversation)

    def generate_proactive_question(self, conversation_id: str, topic: str) -> str:
        """Сгенерировать проактивный вопрос"""
        conversation = self.active_conversations.get(conversation_id)
        language = 'en'
        if conversation and conversation.messages:
            user_messages = [m for m in conversation.messages if m.role == 'user']
            if user_messages:
                language = user_messages[-1].language

        return self.question_generator.generate_question(topic, language)

    def save_conversation(self, conversation_id: str):
        """Сохранить диалог в БД"""
        conversation = self.active_conversations.get(conversation_id)
        if conversation:
            self.memory.save_conversation(conversation)

    def save_all_conversations(self):
        """Сохранить все активные диалоги"""
        for conv_id in self.active_conversations:
            self.save_conversation(conv_id)

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Получить сводку по диалогу"""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            return {}

        total_messages = len(conversation.messages)
        user_messages = [m for m in conversation.messages if m.role == 'user']
        assistant_messages = [m for m in conversation.messages if m.role == 'assistant']

        languages = list(set(m.language for m in conversation.messages if m.language != 'unknown'))
        emotions = list(set(m.emotion for m in conversation.messages if m.emotion))

        return {
            'conversation_id': conversation_id,
            'total_messages': total_messages,
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'languages': languages,
            'emotions': emotions,
            'created_at': conversation.created_at,
            'updated_at': conversation.updated_at,
            'duration_seconds': conversation.updated_at - conversation.created_at
        }


# === ДЕМО ===
if __name__ == "__main__":
    print("🗣️ Демо: Conversation Manager")
    print("=" * 60)

    # Создать менеджер
    manager = ConversationManager(db_path="demo_conversations.db")

    # Начать диалог
    conv_id = "demo_session_001"
    conversation = manager.start_conversation(conv_id, metadata={"user": "test_user"})

    # Симуляция диалога
    dialogs = [
        ("user", "Привет! Помоги мне создать веб-сайт"),
        ("assistant", "Привет! Конечно помогу. Какой сайт хочешь создать? Для бизнеса, портфолио или что-то другое?"),
        ("user", "Для моего стартапа по продаже эко-продуктов"),
        ("assistant", "Отличная идея! Хочешь, я задам несколько вопросов, чтобы лучше понять твои потребности?"),
        ("user", "Давай!"),
        ("assistant", "1. Какой дизайн предпочитаешь: минималистичный или яркий?\n2. Нужна ли интеграция с платёжными системами?\n3. Планируешь блог или только каталог товаров?"),
    ]

    for role, content in dialogs:
        if role == "user":
            msg = manager.add_user_message(conv_id, content)
        else:
            msg = manager.add_assistant_message(conv_id, content)

        print(f"\n[{msg.language.upper()}] {role.upper()}: {content}")

    # Получить контекст для LLM
    print("\n" + "=" * 60)
    print("📋 Контекст для LLM:")
    context = manager.get_context_for_llm(conv_id)
    for msg in context:
        print(f"{msg['role']}: {msg['content'][:100]}...")

    # Сводка
    print("\n" + "=" * 60)
    print("📊 Сводка диалога:")
    summary = manager.get_conversation_summary(conv_id)
    for key, value in summary.items():
        print(f"{key}: {value}")

    # Сохранить
    manager.save_conversation(conv_id)
    print("\n✅ Диалог сохранён в БД!")

    # Тест поиска
    print("\n" + "=" * 60)
    print("🔍 Поиск сообщений с 'сайт':")
    results = manager.memory.search_messages("сайт")
    for conv_id, msg in results:
        print(f"[{conv_id}] {msg.role}: {msg.content[:80]}...")
