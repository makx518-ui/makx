"""
🧠 Intelligent Response Generator - Интеллектуальный генератор ответов
Intent Recognition + Template-based Response + Context-aware Generation

Возможности:
- Определение намерения пользователя (Intent Recognition)
- Умные ответы без LLM
- Контекстно-зависимая генерация
- Мультиязычная поддержка
- Entity extraction
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import random


class Intent(Enum):
    """Типы намерений пользователя"""
    GREETING = "greeting"
    FAREWELL = "farewell"
    GRATITUDE = "gratitude"
    HELP_REQUEST = "help_request"
    QUESTION = "question"
    CREATE_PROJECT = "create_project"
    CREATE_WEBSITE = "create_website"
    CREATE_BOT = "create_bot"
    CREATE_API = "create_api"
    CREATE_GAME = "create_game"
    CODE_REQUEST = "code_request"
    EXPLANATION = "explanation"
    CLARIFICATION = "clarification"
    AFFIRMATION = "affirmation"
    NEGATION = "negation"
    SMALL_TALK = "small_talk"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Результат определения намерения"""
    intent: Intent
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)


class IntentRecognizer:
    """Распознаватель намерений"""

    # Паттерны для определения намерений (мультиязычные)
    INTENT_PATTERNS = {
        Intent.GREETING: {
            'ru': [
                r'\b(привет|здравствуй|здравствуйте|доброе утро|добрый день|добрый вечер|хай|hi|хелло)\b',
                r'\bприв\b',
            ],
            'en': [
                r'\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b',
            ]
        },
        Intent.FAREWELL: {
            'ru': [
                r'\b(пока|до свидания|до встречи|спокойной ночи|увидимся|bye|goodbye)\b',
            ],
            'en': [
                r'\b(bye|goodbye|see you|farewell|good night)\b',
            ]
        },
        Intent.GRATITUDE: {
            'ru': [
                r'\b(спасибо|благодар|спс|thx|thanks)\b',
            ],
            'en': [
                r'\b(thank|thanks|thx|appreciate)\b',
            ]
        },
        Intent.HELP_REQUEST: {
            'ru': [
                r'\b(помо(ги|жешь|гите)|подскажи|помощь|нужна помощь|как .* сделать)\b',
            ],
            'en': [
                r'\b(help|assist|can you help|need help|how to|how do i)\b',
            ]
        },
        Intent.CREATE_WEBSITE: {
            'ru': [
                r'\b(созда(й|ть|дим) .*(сайт|веб|website)|сдела(й|ть) .* сайт)\b',
                r'\b(веб.?сайт|веб.?страниц)\b',
            ],
            'en': [
                r'\b(create|make|build) .*(website|web|site)\b',
            ]
        },
        Intent.CREATE_BOT: {
            'ru': [
                r'\b(созда(й|ть) .* (бот|bot)|сдела(й|ть) .* бот)\b',
                r'\b(telegram|discord) .* бот\b',
            ],
            'en': [
                r'\b(create|make|build) .* (bot|chatbot)\b',
                r'\b(telegram|discord) .* bot\b',
            ]
        },
        Intent.CREATE_API: {
            'ru': [
                r'\b(созда(й|ть) .* api|rest api|сервис)\b',
            ],
            'en': [
                r'\b(create|make|build) .* (api|rest api|service)\b',
            ]
        },
        Intent.CREATE_GAME: {
            'ru': [
                r'\b(созда(й|ть) .* игр|сдела(й|ть) .* игр)\b',
            ],
            'en': [
                r'\b(create|make|build) .* game\b',
            ]
        },
        Intent.QUESTION: {
            'ru': [
                r'\b(что|как|где|когда|почему|зачем|какой|какая|какое)\b.*\?',
                r'.*\?$',
            ],
            'en': [
                r'\b(what|how|where|when|why|which|who)\b.*\?',
                r'.*\?$',
            ]
        },
        Intent.AFFIRMATION: {
            'ru': [
                r'\b(да|ага|угу|конечно|разумеется|okay|ok|хорошо|ладно|yes)\b',
            ],
            'en': [
                r'\b(yes|yeah|yep|sure|of course|okay|ok|alright)\b',
            ]
        },
        Intent.NEGATION: {
            'ru': [
                r'\b(нет|не надо|не нужно|отмена|no)\b',
            ],
            'en': [
                r'\b(no|nope|not|don\'t|cancel)\b',
            ]
        },
    }

    # Ключевые слова для entity extraction
    ENTITY_KEYWORDS = {
        'project_type': {
            'website': ['сайт', 'веб', 'website', 'web', 'webpage'],
            'bot': ['бот', 'bot', 'chatbot'],
            'api': ['api', 'rest', 'service', 'сервис'],
            'game': ['игра', 'игру', 'game'],
            'app': ['приложение', 'app', 'application'],
        },
        'technology': {
            'python': ['python', 'питон', 'пайтон'],
            'javascript': ['javascript', 'js', 'node'],
            'react': ['react', 'реакт'],
            'flask': ['flask', 'фласк'],
            'fastapi': ['fastapi', 'фастапи'],
            'telegram': ['telegram', 'телеграм'],
            'discord': ['discord', 'дискорд'],
        },
        'purpose': {
            'business': ['бизнес', 'business', 'компания', 'company'],
            'personal': ['личный', 'personal', 'для себя'],
            'education': ['обучение', 'education', 'учёба'],
            'entertainment': ['развлечение', 'entertainment', 'игра'],
        }
    }

    def __init__(self):
        pass

    def recognize(self, text: str, language: str = 'ru') -> IntentResult:
        """
        Распознать намерение пользователя

        Args:
            text: Текст пользователя
            language: Язык текста

        Returns:
            IntentResult с намерением, уверенностью и сущностями
        """
        text_lower = text.lower()

        # Попробовать сопоставить с паттернами
        best_intent = Intent.UNKNOWN
        best_confidence = 0.0

        for intent, patterns_dict in self.INTENT_PATTERNS.items():
            patterns = patterns_dict.get(language, []) + patterns_dict.get('en', [])

            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Уверенность зависит от длины совпадения
                    match = re.search(pattern, text_lower, re.IGNORECASE)
                    if match:
                        match_length = len(match.group())
                        confidence = min(0.6 + (match_length / len(text)) * 0.4, 0.95)

                        if confidence > best_confidence:
                            best_intent = intent
                            best_confidence = confidence

        # Извлечь сущности
        entities = self._extract_entities(text_lower)

        # Извлечь ключевые слова
        keywords = self._extract_keywords(text_lower)

        return IntentResult(
            intent=best_intent,
            confidence=best_confidence,
            entities=entities,
            keywords=keywords
        )

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Извлечь сущности из текста"""
        entities = {}

        for entity_type, keywords_dict in self.ENTITY_KEYWORDS.items():
            for entity_value, keywords in keywords_dict.items():
                for keyword in keywords:
                    if keyword in text:
                        entities[entity_type] = entity_value
                        break

        return entities

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечь ключевые слова"""
        # Удалить стоп-слова
        stop_words = {'и', 'в', 'не', 'на', 'с', 'что', 'как', 'это', 'по', 'для',
                     'the', 'is', 'and', 'of', 'to', 'in', 'a', 'for'}

        words = re.findall(r'\w+', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return keywords[:10]  # Топ 10 ключевых слов


class ResponseTemplateEngine:
    """Движок для генерации ответов по шаблонам"""

    # Шаблоны ответов для каждого намерения
    RESPONSE_TEMPLATES = {
        Intent.GREETING: {
            'ru': [
                "Привет{name}! Рад тебя видеть. Чем могу помочь?",
                "Здравствуй{name}! Готов приступить к работе. Какие планы?",
                "Приветствую{name}! Что будем делать сегодня?",
                "Хай{name}! Я готов помогать. Какая задача?",
            ],
            'en': [
                "Hello{name}! Great to see you. How can I help?",
                "Hi{name}! Ready to work. What's the plan?",
                "Hey{name}! What shall we do today?",
            ]
        },
        Intent.FAREWELL: {
            'ru': [
                "До встречи! Обращайся, если что-то понадобится.",
                "Пока! Было приятно помогать.",
                "До свидания! Удачи в проектах!",
            ],
            'en': [
                "See you later! Reach out if you need anything.",
                "Goodbye! It was great helping you.",
                "Bye! Good luck with your projects!",
            ]
        },
        Intent.GRATITUDE: {
            'ru': [
                "Пожалуйста! Всегда рад помочь.",
                "Не за что! Обращайся ещё.",
                "Рад был помочь!",
            ],
            'en': [
                "You're welcome! Always happy to help.",
                "My pleasure! Feel free to ask again.",
                "Glad I could help!",
            ]
        },
        Intent.CREATE_WEBSITE: {
            'ru': [
                "Отлично! Создадим {project_type} для {purpose}. Какой стиль дизайна тебе нравится? Минималистичный или яркий?",
                "Супер! Давай сделаем крутой сайт. Расскажи подробнее, что должно быть на сайте?",
                "Понял! Веб-сайт - это моя специальность. Какие страницы нужны? (главная, о нас, контакты, и т.д.)",
            ],
            'en': [
                "Great! Let's create a {project_type} for {purpose}. What design style do you prefer? Minimalist or vibrant?",
                "Awesome! Let's build a cool website. Tell me more about what should be on the site?",
                "Got it! Websites are my specialty. What pages do you need? (home, about, contact, etc.)",
            ]
        },
        Intent.CREATE_BOT: {
            'ru': [
                "Класс! {project_type} для {technology} - отличная идея. Какие команды должен уметь бот?",
                "Отлично! Создам бота. Какой функционал нужен? (ответы на вопросы, уведомления, и т.д.)",
            ],
            'en': [
                "Cool! A {project_type} for {technology} - great idea. What commands should the bot have?",
                "Excellent! I'll create a bot. What functionality do you need? (Q&A, notifications, etc.)",
            ]
        },
        Intent.QUESTION: {
            'ru': [
                "Отличный вопрос! Давай разберёмся. {context}",
                "Хороший вопрос. Вот что я могу рассказать: {context}",
                "Понял твой вопрос. Объясню подробно: {context}",
            ],
            'en': [
                "Great question! Let's figure it out. {context}",
                "Good question. Here's what I can tell you: {context}",
                "I understand your question. Let me explain: {context}",
            ]
        },
        Intent.HELP_REQUEST: {
            'ru': [
                "Конечно помогу! Что именно нужно сделать?",
                "С радостью помогу. Опиши задачу подробнее.",
                "Я здесь, чтобы помогать! Какая проблема?",
            ],
            'en': [
                "Of course I'll help! What exactly needs to be done?",
                "Happy to help. Describe the task in more detail.",
                "I'm here to help! What's the issue?",
            ]
        },
        Intent.AFFIRMATION: {
            'ru': [
                "Отлично! Тогда приступим.",
                "Супер! Начинаем работу.",
                "Хорошо! Давай сделаем это.",
            ],
            'en': [
                "Great! Let's get started.",
                "Super! Beginning work.",
                "Alright! Let's do this.",
            ]
        },
        Intent.NEGATION: {
            'ru': [
                "Хорошо, понял. Что-то ещё нужно?",
                "Ясно. Могу помочь с чем-то другим?",
            ],
            'en': [
                "Okay, understood. Anything else you need?",
                "Clear. Can I help with something else?",
            ]
        },
    }

    def __init__(self):
        pass

    def generate_response(self, intent_result: IntentResult, language: str = 'ru',
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Сгенерировать ответ на основе намерения

        Args:
            intent_result: Результат распознавания намерения
            language: Язык ответа
            context: Дополнительный контекст

        Returns:
            Сгенерированный ответ
        """
        templates = self.RESPONSE_TEMPLATES.get(intent_result.intent, {})
        lang_templates = templates.get(language, templates.get('en', []))

        if not lang_templates:
            # Fallback ответ
            return self._generate_fallback_response(intent_result, language)

        # Выбрать случайный шаблон
        template = random.choice(lang_templates)

        # Подставить переменные
        variables = self._prepare_variables(intent_result, context)
        response = template.format(**variables)

        return response

    def _prepare_variables(self, intent_result: IntentResult,
                          context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Подготовить переменные для шаблона"""
        variables = {}

        # Имя пользователя
        if context and 'user_name' in context:
            variables['name'] = f", {context['user_name']}"
        else:
            variables['name'] = ""

        # Тип проекта
        variables['project_type'] = intent_result.entities.get('project_type', 'проект')

        # Технология
        variables['technology'] = intent_result.entities.get('technology', 'платформу')

        # Назначение
        variables['purpose'] = intent_result.entities.get('purpose', 'твоих целей')

        # Контекст
        variables['context'] = ""

        # Все переменные должны быть строками
        return {k: str(v) for k, v in variables.items()}

    def _generate_fallback_response(self, intent_result: IntentResult, language: str) -> str:
        """Генерация fallback ответа"""
        fallbacks = {
            'ru': [
                "Понял тебя! Давай разберёмся вместе.",
                "Интересная задача! Расскажи подробнее.",
                "Я готов помочь. Уточни, пожалуйста, детали.",
            ],
            'en': [
                "I understand! Let's figure this out together.",
                "Interesting task! Tell me more.",
                "I'm ready to help. Please clarify the details.",
            ]
        }

        responses = fallbacks.get(language, fallbacks['en'])
        return random.choice(responses)


class IntelligentResponseGenerator:
    """Главный интеллектуальный генератор ответов"""

    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        self.template_engine = ResponseTemplateEngine()

    def generate(self, user_message: str, language: str = 'ru',
                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Сгенерировать интеллектуальный ответ

        Args:
            user_message: Сообщение пользователя
            language: Язык
            context: Контекст (имя пользователя, история и т.д.)

        Returns:
            Dict с ответом и метаданными
        """
        # Распознать намерение
        intent_result = self.intent_recognizer.recognize(user_message, language)

        # Сгенерировать ответ
        response = self.template_engine.generate_response(
            intent_result,
            language,
            context
        )

        return {
            "response": response,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "entities": intent_result.entities,
            "keywords": intent_result.keywords,
        }


# === ДЕМО ===
if __name__ == "__main__":
    print("🧠 Демо: Intelligent Response Generator")
    print("=" * 60)

    generator = IntelligentResponseGenerator()

    test_cases = [
        ("Привет! Как дела?", "ru"),
        ("Помоги создать сайт для моей кофейни", "ru"),
        ("Нужен Telegram бот для приёма заказов", "ru"),
        ("Hello! Can you help me?", "en"),
        ("Create a website for my business", "en"),
        ("Спасибо за помощь!", "ru"),
        ("Что такое Python?", "ru"),
        ("Да, давай сделаем", "ru"),
    ]

    print("\nРезультаты генерации:\n")

    for message, lang in test_cases:
        print(f"👤 User ({lang}): {message}")

        result = generator.generate(message, language=lang, context={"user_name": "Alex"})

        print(f"🤖 AI: {result['response']}")
        print(f"   Intent: {result['intent']} (confidence: {result['confidence']:.2%})")
        if result['entities']:
            print(f"   Entities: {result['entities']}")
        print()

    print("✅ Демо завершено!")
