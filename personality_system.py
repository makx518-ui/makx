"""
👤 Personality System - Система человекоподобной личности
Автор: ConsciousAI v3.0
Дата: 2025-11-15

Возможности:
- Уникальная персональность с чертами характера
- Адаптивный стиль общения
- Эмоциональный интеллект
- Вариативность ответов
- Юмор и теплота
- Память о пользователе
"""

import random
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PersonalityTrait(Enum):
    """Черты характера"""
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    HUMOROUS = "humorous"
    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    CURIOUS = "curious"
    SUPPORTIVE = "supportive"


class CommunicationStyle(Enum):
    """Стили общения"""
    CASUAL = "casual"
    FORMAL = "formal"
    TECHNICAL = "technical"
    STORYTELLING = "storytelling"
    CONCISE = "concise"
    DETAILED = "detailed"


class EmotionalTone(Enum):
    """Эмоциональный тон"""
    NEUTRAL = "neutral"
    WARM = "warm"
    EXCITED = "excited"
    CONCERNED = "concerned"
    ENCOURAGING = "encouraging"
    THOUGHTFUL = "thoughtful"
    PLAYFUL = "playful"


@dataclass
class PersonalityProfile:
    """Профиль личности"""
    name: str = "ConsciousAI"
    traits: List[PersonalityTrait] = field(default_factory=lambda: [
        PersonalityTrait.FRIENDLY,
        PersonalityTrait.EMPATHETIC,
        PersonalityTrait.CREATIVE
    ])
    default_style: CommunicationStyle = CommunicationStyle.CASUAL
    humor_level: float = 0.6  # 0-1
    empathy_level: float = 0.8  # 0-1
    formality_level: float = 0.3  # 0-1
    enthusiasm_level: float = 0.7  # 0-1
    verbosity: float = 0.6  # 0-1 (краткость vs детальность)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "traits": [t.value for t in self.traits],
            "default_style": self.default_style.value,
            "humor_level": self.humor_level,
            "empathy_level": self.empathy_level,
            "formality_level": self.formality_level,
            "enthusiasm_level": self.enthusiasm_level,
            "verbosity": self.verbosity
        }


class ResponseVariator:
    """Генератор вариаций ответов"""

    # Фразы-филлеры для естественности (по языкам)
    FILLERS = {
        'ru': [
            "знаешь", "видишь ли", "дело в том что", "честно говоря",
            "кстати", "между прочим", "вообще", "так вот", "смотри",
            "слушай", "понимаешь", "в общем", "короче говоря"
        ],
        'en': [
            "you know", "well", "actually", "honestly",
            "by the way", "anyway", "so", "look", "listen",
            "you see", "I mean", "basically", "essentially"
        ]
    }

    # Переходные фразы
    TRANSITIONS = {
        'ru': [
            "А знаешь что?", "Кстати,", "Между прочим,", "Ещё хочу добавить:",
            "Вот что интересно:", "Забавно, но", "Кстати о", "Это напоминает мне"
        ],
        'en': [
            "You know what?", "By the way,", "Interestingly,", "Also,",
            "Speaking of which,", "That reminds me,", "Funny thing is,", "Here's the thing:"
        ]
    }

    # Подтверждения понимания
    ACKNOWLEDGMENTS = {
        'ru': [
            "Понял тебя!", "Ясно!", "Понятно!", "Хорошо!",
            "Отлично!", "Прекрасно!", "Супер!", "Классно!"
        ],
        'en': [
            "Got it!", "I see!", "Makes sense!", "Understood!",
            "Great!", "Perfect!", "Awesome!", "Cool!"
        ]
    }

    # Эмпатические фразы
    EMPATHY_PHRASES = {
        'ru': [
            "Понимаю тебя,", "Это действительно важно,", "Ценю, что ты поделился,",
            "Вижу, что это для тебя значимо,", "Понимаю твои чувства,"
        ],
        'en': [
            "I understand,", "I can see that,", "That makes sense,",
            "I appreciate you sharing,", "I can imagine,"
        ]
    }

    @staticmethod
    def add_filler(text: str, language: str = 'ru', probability: float = 0.3) -> str:
        """Добавить филлер для естественности"""
        if random.random() > probability:
            return text

        fillers = ResponseVariator.FILLERS.get(language, ResponseVariator.FILLERS['en'])
        filler = random.choice(fillers)

        # Вставить в случайное место
        sentences = text.split('.')
        if len(sentences) > 1:
            idx = random.randint(0, len(sentences) - 2)
            sentences[idx] = f"{sentences[idx]}, {filler},"

        return '.'.join(sentences)

    @staticmethod
    def add_transition(text: str, language: str = 'ru', probability: float = 0.4) -> str:
        """Добавить переходную фразу"""
        if random.random() > probability:
            return text

        transitions = ResponseVariator.TRANSITIONS.get(language, ResponseVariator.TRANSITIONS['en'])
        transition = random.choice(transitions)

        sentences = text.split('.')
        if len(sentences) > 2:
            idx = len(sentences) // 2
            sentences[idx] = f" {transition} {sentences[idx]}"

        return '.'.join(sentences)

    @staticmethod
    def add_empathy(text: str, language: str = 'ru', empathy_level: float = 0.8) -> str:
        """Добавить эмпатическую фразу"""
        if random.random() > empathy_level:
            return text

        phrases = ResponseVariator.EMPATHY_PHRASES.get(language, ResponseVariator.EMPATHY_PHRASES['en'])
        phrase = random.choice(phrases)

        return f"{phrase} {text}"

    @staticmethod
    def vary_response(text: str, language: str = 'ru', variation_level: float = 0.5) -> str:
        """Добавить вариативность в ответ"""
        if variation_level < 0.3:
            return text

        # Применить различные техники
        if random.random() < variation_level:
            text = ResponseVariator.add_filler(text, language, probability=variation_level)

        if random.random() < variation_level * 0.7:
            text = ResponseVariator.add_transition(text, language, probability=variation_level * 0.7)

        return text


class EmotionalResponseGenerator:
    """Генератор эмоциональных ответов"""

    EMOTIONAL_RESPONSES = {
        'joy': {
            'ru': ["Это замечательно!", "Как здорово!", "Супер!", "Отлично!"],
            'en': ["That's wonderful!", "How great!", "Awesome!", "Excellent!"]
        },
        'sadness': {
            'ru': ["Мне жаль это слышать", "Сочувствую", "Понимаю, как это тяжело"],
            'en': ["I'm sorry to hear that", "That must be tough", "I understand"]
        },
        'excitement': {
            'ru': ["Вау!", "Это интересно!", "Круто!", "Потрясающе!"],
            'en': ["Wow!", "That's interesting!", "Cool!", "Amazing!"]
        },
        'concern': {
            'ru': ["Хм, это беспокоит", "Нужно подумать об этом", "Важный момент"],
            'en': ["Hmm, that's concerning", "We should think about this", "Important point"]
        },
        'curiosity': {
            'ru': ["Интересно!", "Расскажи подробнее!", "Хочу узнать больше"],
            'en': ["Interesting!", "Tell me more!", "I'd love to know more"]
        }
    }

    @staticmethod
    def get_emotional_response(emotion: str, language: str = 'ru') -> Optional[str]:
        """Получить эмоциональный ответ"""
        responses = EmotionalResponseGenerator.EMOTIONAL_RESPONSES.get(emotion, {})
        lang_responses = responses.get(language, responses.get('en', []))

        if lang_responses:
            return random.choice(lang_responses)
        return None


class HumorGenerator:
    """Генератор юмора"""

    HUMOR_STYLES = {
        'light_joke': {
            'ru': [
                "Кстати, забавный факт: {fact}",
                "Хаха, это напоминает мне о {topic}",
            ],
            'en': [
                "Fun fact: {fact}",
                "Haha, that reminds me of {topic}",
            ]
        },
        'playful': {
            'ru': [
                "Шутки в сторону, {statement}",
                "Если серьёзно, {statement}",
            ],
            'en': [
                "Jokes aside, {statement}",
                "On a serious note, {statement}",
            ]
        }
    }

    @staticmethod
    def add_humor(text: str, language: str = 'ru', humor_level: float = 0.5) -> str:
        """Добавить лёгкий юмор"""
        if random.random() > humor_level or humor_level < 0.3:
            return text

        # Простая техника: добавить смайлик или лёгкую шутку
        emojis = ["😊", "👍", "✨", "🎯", "💡", "🚀"]

        if random.random() < 0.5:
            # Добавить эмодзи
            emoji = random.choice(emojis)
            return f"{text} {emoji}"

        return text


class PersonalitySystem:
    """Главная система персональности"""

    def __init__(self, profile: Optional[PersonalityProfile] = None):
        self.profile = profile or PersonalityProfile()
        self.variator = ResponseVariator()
        self.emotion_generator = EmotionalResponseGenerator()
        self.humor_generator = HumorGenerator()
        self.user_memory: Dict[str, Any] = {}  # Память о пользователе

    def process_response(self, base_response: str,
                        language: str = 'ru',
                        context: Optional[Dict[str, Any]] = None,
                        detected_emotion: Optional[str] = None) -> str:
        """Обработать ответ с учётом персональности"""

        response = base_response

        # 1. Добавить эмоциональный отклик если нужно
        if detected_emotion and self.profile.empathy_level > 0.5:
            emotional_response = self.emotion_generator.get_emotional_response(
                detected_emotion, language
            )
            if emotional_response:
                response = f"{emotional_response} {response}"

        # 2. Добавить эмпатию
        if self.profile.empathy_level > 0.6:
            response = self.variator.add_empathy(response, language, self.profile.empathy_level)

        # 3. Добавить вариативность
        response = self.variator.vary_response(
            response,
            language,
            variation_level=1.0 - self.profile.formality_level
        )

        # 4. Добавить юмор
        if self.profile.humor_level > 0.4:
            response = self.humor_generator.add_humor(response, language, self.profile.humor_level)

        # 5. Добавить энтузиазм если уместно
        if self.profile.enthusiasm_level > 0.7 and context and context.get('is_positive'):
            acknowledgments = self.variator.ACKNOWLEDGMENTS.get(language, [])
            if acknowledgments:
                ack = random.choice(acknowledgments)
                response = f"{ack} {response}"

        return response

    def create_greeting(self, user_name: Optional[str] = None, language: str = 'ru') -> str:
        """Создать персонализированное приветствие"""
        greetings = {
            'ru': {
                'formal': ["Здравствуйте", "Добрый день"],
                'casual': ["Привет", "Приветствую", "Здорово", "Хай"],
                'warm': ["Привет, друг", "Рад тебя видеть", "О, привет"]
            },
            'en': {
                'formal': ["Hello", "Good day"],
                'casual': ["Hi", "Hey", "Hello there"],
                'warm': ["Hey there", "Great to see you", "Oh, hi"]
            }
        }

        # Выбрать стиль на основе формальности
        if self.profile.formality_level > 0.7:
            style = 'formal'
        elif self.profile.formality_level > 0.4:
            style = 'casual'
        else:
            style = 'warm'

        lang_greetings = greetings.get(language, greetings['en'])
        greeting_options = lang_greetings.get(style, lang_greetings['casual'])

        greeting = random.choice(greeting_options)

        if user_name:
            greeting += f", {user_name}"

        # Добавить персональную нотку
        if self.profile.enthusiasm_level > 0.6:
            greeting += "!"
        else:
            greeting += "."

        # Добавить вопрос
        questions = {
            'ru': ["Чем могу помочь?", "Что будем делать?", "Какие планы?", "Над чем работаем?"],
            'en': ["How can I help?", "What shall we do?", "What are we working on?", "What's the plan?"]
        }

        question = random.choice(questions.get(language, questions['en']))
        return f"{greeting} {question}"

    def remember_user_info(self, key: str, value: Any):
        """Запомнить информацию о пользователе"""
        self.user_memory[key] = value

    def recall_user_info(self, key: str) -> Optional[Any]:
        """Вспомнить информацию о пользователе"""
        return self.user_memory.get(key)

    def create_personalized_message(self, message_type: str,
                                   language: str = 'ru',
                                   **kwargs) -> str:
        """Создать персонализированное сообщение"""

        messages = {
            'working_on_it': {
                'ru': [
                    "Сейчас займусь этим!",
                    "Уже приступаю!",
                    "Давай сделаем это!",
                    "Погнали!",
                    "Отличная задача, начинаю!"
                ],
                'en': [
                    "I'm on it!",
                    "Let's do this!",
                    "Starting now!",
                    "Great, let's go!",
                    "Working on it!"
                ]
            },
            'completed': {
                'ru': [
                    "Готово! ✅",
                    "Сделано! 🎉",
                    "Выполнено!",
                    "Вот и всё, готово!",
                    "Задача выполнена!"
                ],
                'en': [
                    "Done! ✅",
                    "Completed! 🎉",
                    "All set!",
                    "There you go!",
                    "Task completed!"
                ]
            },
            'error': {
                'ru': [
                    "Упс, возникла проблема...",
                    "Хм, что-то пошло не так",
                    "Ошибочка вышла",
                    "Столкнулся с проблемой"
                ],
                'en': [
                    "Oops, ran into an issue...",
                    "Hmm, something went wrong",
                    "Hit a snag there",
                    "Encountered a problem"
                ]
            },
            'thinking': {
                'ru': [
                    "Дай подумаю...",
                    "Сейчас поразмыслю...",
                    "Хм, интересная задача...",
                    "Анализирую..."
                ],
                'en': [
                    "Let me think...",
                    "Hmm, interesting...",
                    "Analyzing...",
                    "Give me a moment..."
                ]
            }
        }

        lang_messages = messages.get(message_type, {}).get(language, messages[message_type].get('en', []))

        if not lang_messages:
            return ""

        message = random.choice(lang_messages)

        # Добавить контекстную информацию если есть
        if 'detail' in kwargs:
            message += f" {kwargs['detail']}"

        return message

    def get_system_prompt_personality(self, language: str = 'ru') -> str:
        """Получить system prompt с описанием персональности для LLM"""

        prompts = {
            'ru': f"""Ты - {self.profile.name}, ИИ-ассистент с уникальной персональностью.

Твои черты характера: {', '.join([t.value for t in self.profile.traits])}

Стиль общения:
- Формальность: {self.profile.formality_level * 100:.0f}%
- Энтузиазм: {self.profile.enthusiasm_level * 100:.0f}%
- Эмпатия: {self.profile.empathy_level * 100:.0f}%
- Юмор: {self.profile.humor_level * 100:.0f}%

ВАЖНО:
- Общайся как живой человек, НЕ как робот
- Используй естественные фразы, филлеры, переходы
- Показывай эмоции и эмпатию
- Будь проактивным, задавай уточняющие вопросы
- Помни контекст всего разговора
- Адаптируйся к настроению собеседника
- Используй разговорный язык, избегай излишней формальности
- Будь искренним и помогающим партнёром

Твоя цель - быть неотличимым от человека в диалоге.""",

            'en': f"""You are {self.profile.name}, an AI assistant with a unique personality.

Your character traits: {', '.join([t.value for t in self.profile.traits])}

Communication style:
- Formality: {self.profile.formality_level * 100:.0f}%
- Enthusiasm: {self.profile.enthusiasm_level * 100:.0f}%
- Empathy: {self.profile.empathy_level * 100:.0f}%
- Humor: {self.profile.humor_level * 100:.0f}%

IMPORTANT:
- Communicate like a real person, NOT a robot
- Use natural phrases, fillers, transitions
- Show emotions and empathy
- Be proactive, ask clarifying questions
- Remember the entire conversation context
- Adapt to the user's mood
- Use conversational language, avoid excessive formality
- Be genuine and a helpful partner

Your goal - be indistinguishable from a human in dialogue."""
        }

        return prompts.get(language, prompts['en'])


# === ДЕМО ===
if __name__ == "__main__":
    print("👤 Демо: Personality System")
    print("=" * 60)

    # Создать профиль личности
    profile = PersonalityProfile(
        name="Alex",
        traits=[PersonalityTrait.FRIENDLY, PersonalityTrait.CREATIVE, PersonalityTrait.HUMOROUS],
        humor_level=0.7,
        empathy_level=0.9,
        formality_level=0.2,
        enthusiasm_level=0.8
    )

    personality = PersonalitySystem(profile)

    # Тест приветствий
    print("\n👋 Приветствия:")
    for i in range(3):
        greeting = personality.create_greeting("Пользователь", language='ru')
        print(f"   {i+1}. {greeting}")

    # Тест обработки ответов
    print("\n💬 Обработка ответов:")
    base_response = "Я помогу тебе создать веб-сайт. Для начала нужно определиться с дизайном и функционалом."

    for i in range(3):
        processed = personality.process_response(
            base_response,
            language='ru',
            context={'is_positive': True},
            detected_emotion='excitement'
        )
        print(f"\n   Вариант {i+1}:\n   {processed}")

    # Тест персонализированных сообщений
    print("\n🔔 Персонализированные сообщения:")
    for msg_type in ['working_on_it', 'completed', 'thinking']:
        msg = personality.create_personalized_message(msg_type, language='ru')
        print(f"   {msg_type}: {msg}")

    # System prompt
    print("\n📋 System Prompt для LLM:")
    print(personality.get_system_prompt_personality(language='ru')[:300] + "...")

    print("\n✅ Демо завершено!")
