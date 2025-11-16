"""
🌟 ConsciousAI Ultimate - Полная интеграция всех систем
Автор: ConsciousAI v4.2
Дата: 2025-11-15

Возможности:
- Мультиязычные человекоподобные диалоги
- Автономное выполнение проектов
- Работа с инструментами (файлы, git, shell, web)
- Интеграция с LLM (GPT-4, Claude)
- Эмоциональный интеллект
- Персональность и стиль общения
- Создание проектов под ключ
- Self-correction и адаптивное обучение
- Маркетинговая автоматизация 24/7 (v4.2)
- Автономное продвижение в соцсетях
- AI-генерация продающих текстов
- Автопоиск площадок и рассылки
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import sys

# Импорты наших модулей
from conversation_manager import (
    ConversationManager,
    LanguageDetector,
    Message
)
from personality_system import (
    PersonalitySystem,
    PersonalityProfile,
    PersonalityTrait,
    CommunicationStyle
)
from agent_framework import (
    AutonomousAgent,
    TaskPlanner,
    ToolRegistry,
    SelfCorrectionSystem
)
from tool_executor import ToolExecutor
from project_generator import ProjectGenerator, ProjectConfig, ProjectType
from llm_integration import (
    LLMManager,
    create_llm_provider,
    LLMConfig
)

# Новые улучшенные модули v4.1
from enhanced_language_detector import EnhancedLanguageDetector, detect_language
from intelligent_response_generator import IntelligentResponseGenerator
from retry_handler import retry_with_backoff, RetryConfig
from caching_system import CacheManager, cached
from project_validator import ProjectValidator

# Модули маркетинговой автоматизации v4.2
from marketing_automation_agent import (
    MarketingAutomationAgent,
    Project as MarketingProject,
    Campaign,
    CampaignType
)
from social_media_manager import SocialMediaManager, Platform
from marketing_content_generator import (
    MarketingContentGenerator,
    ContentRequest,
    ContentType,
    ToneOfVoice
)
from marketing_analytics_tracker import MarketingAnalyticsTracker, MetricType
from marketing_outreach_scheduler import OutreachBot, CampaignScheduler

# Импорты из базовых систем (если доступны)
try:
    from conscious_ai_advanced import (
        AdvancedConsciousAI,
        PersistentMemory,
        TranscendentThinking
    )
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False
    print("⚠️ Advanced ConsciousAI не найден, используется базовый функционал")


@dataclass
class UltimateConfig:
    """Конфигурация Ultimate системы"""
    # Персональность
    personality_name: str = "ConsciousAI"
    personality_traits: List[str] = None
    humor_level: float = 0.7
    empathy_level: float = 0.9
    formality_level: float = 0.2

    # LLM
    use_llm: bool = False
    llm_provider: str = "openai"  # 'openai' или 'anthropic'
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_temperature: float = 0.7

    # Функционал
    enable_autonomous_agent: bool = True
    enable_project_generation: bool = True
    enable_advanced_features: bool = True

    # Хранилище
    conversation_db: str = "ultimate_conversations.db"
    memory_db: str = "ultimate_memory.db"


class ConsciousAI_Ultimate:
    """Финальная Ultimate система"""

    def __init__(self, config: Optional[UltimateConfig] = None):
        self.config = config or UltimateConfig()

        print("🌟 Инициализация ConsciousAI Ultimate v4.0...")

        # 1. Conversation Manager
        print("   💬 Загружаю систему диалогов...")
        self.conversation_manager = ConversationManager(
            db_path=self.config.conversation_db
        )

        # 2. Personality System
        print("   👤 Настраиваю персональность...")
        personality_profile = PersonalityProfile(
            name=self.config.personality_name,
            traits=self._parse_personality_traits(),
            humor_level=self.config.humor_level,
            empathy_level=self.config.empathy_level,
            formality_level=self.config.formality_level
        )
        self.personality = PersonalitySystem(personality_profile)

        # 3. Tool Executor
        print("   🛠️ Регистрирую инструменты...")
        self.tool_executor = ToolExecutor()
        self.tool_registry = self._setup_tool_registry()

        # 4. LLM Integration
        self.llm_manager = None
        if self.config.use_llm:
            print(f"   🤖 Подключаю LLM ({self.config.llm_provider})...")
            self.llm_manager = self._setup_llm()

        # 5. Autonomous Agent
        self.agent = None
        if self.config.enable_autonomous_agent:
            print("   🎯 Создаю автономного агента...")
            task_planner = TaskPlanner(
                llm_provider=self.llm_manager.get_provider('primary') if self.llm_manager else None
            )
            self_correction = SelfCorrectionSystem(
                llm_provider=self.llm_manager.get_provider('primary') if self.llm_manager else None
            )
            self.agent = AutonomousAgent(
                tool_registry=self.tool_registry,
                task_planner=task_planner,
                self_correction=self_correction
            )

        # 6. Project Generator
        self.project_generator = None
        if self.config.enable_project_generation:
            print("   🏗️ Готовлю генератор проектов...")
            self.project_generator = ProjectGenerator()

        # 7. Advanced Features (если доступны)
        self.advanced_ai = None
        if self.config.enable_advanced_features and ADVANCED_AVAILABLE:
            print("   ✨ Активирую расширенные возможности...")
            try:
                self.advanced_ai = AdvancedConsciousAI(db_path=self.config.memory_db)
            except Exception as e:
                print(f"   ⚠️ Не удалось загрузить расширенные функции: {e}")

        # 8. Улучшенные компоненты v4.1
        print("   🚀 Активирую улучшения v4.1...")
        self.enhanced_language_detector = EnhancedLanguageDetector()
        self.intelligent_response_generator = IntelligentResponseGenerator()
        self.cache_manager = CacheManager()
        self.project_validator = ProjectValidator()
        print("      ✓ Enhanced Language Detector (99%+ точность)")
        print("      ✓ Intelligent Response Generator (Intent Recognition)")
        print("      ✓ Caching System (LRU + Redis support)")
        print("      ✓ Project Validator (Syntax + Lint + Security)")

        # 9. Маркетинговая автоматизация v4.2
        print("   📱 Активирую маркетинговую автоматизацию v4.2...")
        self.marketing_agent = MarketingAutomationAgent()
        self.content_generator = MarketingContentGenerator()
        self.analytics_tracker = MarketingAnalyticsTracker()
        self.outreach_bot = OutreachBot()
        self.campaign_scheduler = CampaignScheduler()

        # Подключить модули к главному агенту
        self.marketing_agent.content_generator = self.content_generator
        self.marketing_agent.analytics_tracker = self.analytics_tracker
        self.marketing_agent.outreach_bot = self.outreach_bot
        self.marketing_agent.campaign_scheduler = self.campaign_scheduler

        print("      ✓ Marketing Automation Agent (24/7 автомаркетолог)")
        print("      ✓ Content Generator (продажные тексты, статьи, SEO)")
        print("      ✓ Analytics Tracker (метрики, A/B тесты, ROI)")
        print("      ✓ Outreach Bot (автопоиск площадок)")
        print("      ✓ Campaign Scheduler (автопостинг по расписанию)")

        # 9. Текущая сессия
        self.current_conversation_id = None
        self.language_detector = LanguageDetector()  # Fallback

        print("✅ ConsciousAI Ultimate v4.1 готов к работе!\n")

    def _parse_personality_traits(self) -> List[PersonalityTrait]:
        """Парсинг черт характера"""
        if not self.config.personality_traits:
            return [
                PersonalityTrait.FRIENDLY,
                PersonalityTrait.CREATIVE,
                PersonalityTrait.EMPATHETIC
            ]

        traits = []
        for trait_str in self.config.personality_traits:
            try:
                trait = PersonalityTrait[trait_str.upper()]
                traits.append(trait)
            except KeyError:
                print(f"   ⚠️ Неизвестная черта характера: {trait_str}")

        return traits if traits else [PersonalityTrait.FRIENDLY]

    def _setup_llm(self) -> LLMManager:
        """Настройка LLM"""
        manager = LLMManager()

        try:
            provider = create_llm_provider(
                provider=self.config.llm_provider,
                api_key=self.config.llm_api_key,
                model=self.config.llm_model,
                temperature=self.config.llm_temperature
            )
            manager.add_provider('primary', provider)
            print(f"      ✓ {self.config.llm_provider} подключён")

        except Exception as e:
            print(f"      ✗ Ошибка подключения LLM: {e}")

        return manager

    def _setup_tool_registry(self) -> ToolRegistry:
        """Регистрация всех инструментов"""
        registry = ToolRegistry()

        # Получить все инструменты
        all_tools = self.tool_executor.get_all_tools()

        # Зарегистрировать файловые инструменты
        for name, tool in all_tools['file'].items():
            registry.register(name, tool)

        # Git инструменты
        for name, tool in all_tools['git'].items():
            registry.register(name, tool)

        # Shell инструменты
        for name, tool in all_tools['shell'].items():
            registry.register(name, tool)

        # Web инструменты
        for name, tool in all_tools['web'].items():
            registry.register(name, tool)

        # Code инструменты
        for name, tool in all_tools['code'].items():
            registry.register(name, tool)

        # Project инструменты
        for name, tool in all_tools['project'].items():
            registry.register(name, tool)

        print(f"      ✓ Зарегистрировано инструментов: {len(registry.list_tools())}")

        return registry

    async def chat(self, user_message: str, conversation_id: Optional[str] = None) -> str:
        """Основной метод для диалога"""

        # Определить conversation_id
        if conversation_id:
            self.current_conversation_id = conversation_id
        elif not self.current_conversation_id:
            import uuid
            self.current_conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

        conv_id = self.current_conversation_id

        # Определить язык с помощью Enhanced детектора
        language, lang_confidence = self.enhanced_language_detector.detect(user_message, with_confidence=True)

        # Добавить сообщение пользователя
        user_msg = self.conversation_manager.add_user_message(
            conv_id,
            user_message
        )

        # Обновить язык если уверенность высокая
        if lang_confidence > 0.8:
            user_msg.language = language
        else:
            language = user_msg.language

        # Сгенерировать ответ
        if self.llm_manager:
            # Использовать LLM для генерации ответа
            context = self.conversation_manager.get_context_for_llm(conv_id)

            # Добавить system prompt с персональностью
            if context and len(context) > 0:
                context[0]['content'] = self.personality.get_system_prompt_personality(language)

            provider = self.llm_manager.get_provider('primary')
            if provider:
                try:
                    base_response = await provider.generate_with_messages(context)
                except:
                    base_response = "Извините, произошла ошибка при генерации ответа."
            else:
                base_response = "LLM провайдер не настроен."

        else:
            # Простой ответ без LLM
            base_response = self._generate_simple_response(user_message, language)

        # Обработать через personality system
        final_response = self.personality.process_response(
            base_response,
            language=language,
            context={'is_positive': True}
        )

        # Добавить ответ ассистента
        self.conversation_manager.add_assistant_message(
            conv_id,
            final_response
        )

        # Сохранить диалог
        self.conversation_manager.save_conversation(conv_id)

        return final_response

    def _generate_simple_response(self, message: str, language: str) -> str:
        """Умный ответ без LLM (с Intent Recognition)"""
        # Использовать Intelligent Response Generator v4.1
        result = self.intelligent_response_generator.generate(
            user_message=message,
            language=language,
            context={
                "user_name": None,  # TODO: Добавить извлечение имени из памяти
                "conversation_history": []
            }
        )

        return result['response']

    async def execute_task(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Автономное выполнение задачи"""
        if not self.agent:
            return {
                "success": False,
                "error": "Автономный агент не активирован"
            }

        print(f"\n🎯 Начинаю выполнение задачи: {goal}")

        report = await self.agent.execute_goal(goal, context)

        print(f"\n✅ Задача выполнена!")
        print(f"   Прогресс: {report['progress']['percent']:.1f}%")
        print(f"   Выполнено: {report['progress']['completed']} / {report['progress']['total']}")

        return report

    async def create_project(self, config: ProjectConfig) -> Dict[str, Any]:
        """Создать проект под ключ"""
        if not self.project_generator:
            return {
                "success": False,
                "error": "Генератор проектов не активирован"
            }

        print(f"\n🏗️ Создаю проект: {config.name}")

        result = await self.project_generator.generate_project(config)

        if result['success']:
            print(f"\n✅ Проект создан: {result['project_path']}")

            # Автоматическая валидация проекта (v4.1)
            print(f"\n🔍 Запускаю автоматическую валидацию...")
            validation_result = self.project_validator.validate_project(result['project_path'])

            result['validation'] = validation_result
            print(f"   Score: {validation_result['score']}/100")
            print(f"   Status: {'✅ PASSED' if validation_result['passed'] else '⚠️ NEEDS REVIEW'}")

        return result

    def get_available_tools(self) -> List[str]:
        """Получить список доступных инструментов"""
        if self.tool_registry:
            return self.tool_registry.list_tools()
        return []

    def get_conversation_summary(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Получить сводку диалога"""
        conv_id = conversation_id or self.current_conversation_id
        if not conv_id:
            return {}

        return self.conversation_manager.get_conversation_summary(conv_id)

    async def launch_marketing_campaign(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        unique_selling_points: List[str],
        keywords: List[str],
        platforms: List[str],
        duration_days: int = 30,
        social_media_credentials: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Запустить автономную маркетинговую кампанию 24/7

        Args:
            product_name: Название продукта
            product_description: Описание
            target_audience: Целевая аудитория
            unique_selling_points: Уникальные преимущества
            keywords: Ключевые слова
            platforms: Платформы (twitter, vk, telegram, facebook, reddit)
            duration_days: Длительность кампании
            social_media_credentials: API ключи для соцсетей

        Returns:
            Информация о запущенной кампании
        """
        print(f"\n🚀 Запуск маркетинговой кампании для {product_name}")

        # Создать маркетинговый проект
        marketing_project = MarketingProject(
            name=product_name,
            description=product_description,
            target_audience=target_audience,
            keywords=keywords,
            unique_selling_points=unique_selling_points,
            project_type="product",
            tags=keywords
        )

        # Конвертировать платформы
        platform_enums = []
        for platform_str in platforms:
            try:
                platform_enums.append(Platform[platform_str.upper()])
            except KeyError:
                print(f"⚠️ Неизвестная платформа: {platform_str}")

        # Создать кампанию
        campaign = await self.marketing_agent.create_campaign(
            project=marketing_project,
            campaign_type=CampaignType.PRODUCT_LAUNCH,
            platforms=platform_enums,
            duration_days=duration_days
        )

        print(f"✅ Кампания создана: {campaign.id}")
        print(f"   Платформы: {[p.value for p in platform_enums]}")

        # Если предоставлены credentials - настроить Social Media Manager
        if social_media_credentials:
            credentials_converted = {}
            for platform_str, creds in social_media_credentials.items():
                try:
                    platform_enum = Platform[platform_str.upper()]
                    credentials_converted[platform_enum] = creds
                except KeyError:
                    pass

            if credentials_converted:
                social_manager = SocialMediaManager(credentials_converted)
                self.marketing_agent.social_media_manager = social_manager
                print(f"   ✓ Social Media Manager настроен для {len(credentials_converted)} платформ")

        # Генерировать начальный контент
        print("\n📝 Генерация контента...")
        content_request = ContentRequest(
            content_type=ContentType.SALES_COPY,
            product_name=product_name,
            product_description=product_description,
            target_audience=target_audience,
            unique_selling_points=unique_selling_points,
            keywords=keywords,
            tone=ToneOfVoice.ENTHUSIASTIC,
            language="ru"
        )

        sales_copy = await self.content_generator.generate(content_request)
        print(f"✅ Контент сгенерирован: {len(sales_copy.content)} символов")

        # Найти площадки для аутрича
        print("\n🔍 Поиск площадок для продвижения...")
        targets = await self.outreach_bot.find_platforms(
            keywords=keywords,
            target_audience=target_audience,
            platform_types=["reddit", "telegram", "forum"]
        )
        print(f"✅ Найдено площадок: {len(targets)}")

        # Вернуть информацию о кампании
        return {
            "success": True,
            "campaign_id": campaign.id,
            "platforms": [p.value for p in platform_enums],
            "duration_days": duration_days,
            "generated_content": sales_copy.content,
            "outreach_targets": len(targets),
            "message": f"Маркетинговая кампания запущена! ID: {campaign.id}"
        }

    def save_all(self):
        """Сохранить все данные"""
        print("\n💾 Сохраняю данные...")
        self.conversation_manager.save_all_conversations()
        print("✅ Данные сохранены!")


# === ДЕМО ===
async def demo():
    """Демо Ultimate системы"""
    print("=" * 70)
    print("🌟 DEMO: ConsciousAI Ultimate v4.0")
    print("=" * 70)

    # Создать конфигурацию
    config = UltimateConfig(
        personality_name="Alex",
        personality_traits=["friendly", "creative", "enthusiastic"],
        humor_level=0.7,
        empathy_level=0.9,
        formality_level=0.2,
        use_llm=False,  # Для демо без LLM
        enable_autonomous_agent=True,
        enable_project_generation=True
    )

    # Создать систему
    ai = ConsciousAI_Ultimate(config)

    # === ДЕМО 1: Диалог ===
    print("\n" + "=" * 70)
    print("ДЕМО 1: Мультиязычный диалог")
    print("=" * 70)

    dialogs = [
        ("Привет! Как дела?", "ru"),
        ("Можешь помочь мне создать веб-сайт?", "ru"),
        ("Спасибо за помощь!", "ru"),
    ]

    for user_msg, lang in dialogs:
        print(f"\n👤 Пользователь: {user_msg}")
        response = await ai.chat(user_msg)
        print(f"🤖 AI: {response}")

    # === ДЕМО 2: Автономное выполнение задачи ===
    print("\n" + "=" * 70)
    print("ДЕМО 2: Автономное выполнение задачи")
    print("=" * 70)

    task_result = await ai.execute_task(
        "Создать простой веб-сайт для стартапа",
        context={"theme": "eco-products"}
    )

    print(f"\nРезультат:")
    print(json.dumps(task_result['progress'], ensure_ascii=False, indent=2))

    # === ДЕМО 3: Создание проекта ===
    print("\n" + "=" * 70)
    print("ДЕМО 3: Создание проекта под ключ")
    print("=" * 70)

    project_config = ProjectConfig(
        name="demo_bot",
        project_type=ProjectType.TELEGRAM_BOT,
        description="Telegram бот для демонстрации",
        features=["Команды", "Ответы на сообщения"],
        tech_stack=["Python", "python-telegram-bot"],
        target_directory="./ultimate_demo_projects"
    )

    project_result = await ai.create_project(project_config)
    print(f"\nСоздано файлов: {len(project_result.get('files_created', []))}")

    # === ДЕМО 4: Сводка ===
    print("\n" + "=" * 70)
    print("ДЕМО 4: Сводка системы")
    print("=" * 70)

    print(f"\nДоступные инструменты: {len(ai.get_available_tools())}")
    print(f"Сводка диалога:")
    summary = ai.get_conversation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Сохранить всё
    ai.save_all()

    print("\n" + "=" * 70)
    print("✅ ДЕМО ЗАВЕРШЕНО!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo())
