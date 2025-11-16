"""
✍️ Marketing Content Generator - AI-генератор маркетингового контента

Типы контента:
- Продающие тексты (Sales Copy)
- Статьи для блогов (SEO-оптимизированные)
- Посты для соцсетей
- Email-рассылки
- Landing Page тексты
- Рекламные креативы
- Пресс-релизы

Фичи:
- Адаптация под разные платформы
- SEO-оптимизация (keywords, meta, headings)
- A/B тестирование заголовков
- Tone of voice адаптация
- Мультиязычность
"""

import random
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Типы контента"""
    SALES_COPY = "sales_copy"
    BLOG_ARTICLE = "blog_article"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    LANDING_PAGE = "landing_page"
    AD_CREATIVE = "ad_creative"
    PRESS_RELEASE = "press_release"


class ToneOfVoice(Enum):
    """Тон голоса"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    AUTHORITATIVE = "authoritative"
    CASUAL = "casual"
    HUMOROUS = "humorous"


class Platform(Enum):
    """Платформы"""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    REDDIT = "reddit"
    TELEGRAM = "telegram"
    VK = "vk"
    BLOG = "blog"
    EMAIL = "email"


@dataclass
class ContentRequest:
    """Запрос на генерацию контента"""
    content_type: ContentType
    product_name: str
    product_description: str
    target_audience: str
    unique_selling_points: List[str]
    keywords: List[str] = field(default_factory=list)
    tone: ToneOfVoice = ToneOfVoice.FRIENDLY
    platform: Optional[Platform] = None
    language: str = "ru"
    min_length: int = 0
    max_length: int = 0


@dataclass
class GeneratedContent:
    """Сгенерированный контент"""
    content: str
    headline: str
    call_to_action: str
    hashtags: List[str] = field(default_factory=list)
    seo_metadata: Dict[str, str] = field(default_factory=dict)
    variants: List[str] = field(default_factory=list)  # A/B тест варианты


class MarketingContentGenerator:
    """
    AI-генератор маркетингового контента

    Генерирует продающие тексты, статьи, посты без использования LLM API,
    используя продвинутые шаблоны и комбинаторику.
    """

    # Шаблоны продающих заголовков
    SALES_HEADLINES = {
        "ru": [
            "{product} - {usp}",
            "Откройте для себя {product}: {usp}",
            "Как {product} помогает {benefit}",
            "{number} причин попробовать {product}",
            "Революция в {category}: знакомьтесь, {product}",
            "{product} - решение, которое вы искали",
            "Почему {audience} выбирают {product}",
            "Познакомьтесь с {product} - {usp}",
        ],
        "en": [
            "{product} - {usp}",
            "Discover {product}: {usp}",
            "How {product} helps you {benefit}",
            "{number} reasons to try {product}",
            "Revolutionary {category}: meet {product}",
            "{product} - the solution you've been looking for",
            "Why {audience} choose {product}",
            "Meet {product} - {usp}",
        ]
    }

    # Шаблоны призывов к действию
    CALL_TO_ACTIONS = {
        "ru": [
            "Попробуйте бесплатно",
            "Узнать больше",
            "Начать сейчас",
            "Получить доступ",
            "Присоединиться",
            "Скачать бесплатно",
            "Зарегистрироваться",
            "Попробовать бесплатно 14 дней",
        ],
        "en": [
            "Try for free",
            "Learn more",
            "Get started now",
            "Get access",
            "Join now",
            "Download free",
            "Sign up",
            "Start free 14-day trial",
        ]
    }

    # Структура продающего текста
    SALES_COPY_STRUCTURE = {
        "ru": {
            "problem": "Устали от {pain_point}?",
            "solution": "{product} - это {solution_description}.",
            "benefits": "С {product} вы сможете:\n{benefits_list}",
            "social_proof": "Более {number} пользователей уже доверяют {product}.",
            "cta": "{cta} и {benefit} уже сегодня!",
        },
        "en": {
            "problem": "Tired of {pain_point}?",
            "solution": "{product} is {solution_description}.",
            "benefits": "With {product} you can:\n{benefits_list}",
            "social_proof": "Over {number} users already trust {product}.",
            "cta": "{cta} and {benefit} today!",
        }
    }

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Опциональный LLM клиент для AI-генерации
        """
        self.llm_client = llm_client
        logger.info("✍️ Marketing Content Generator инициализирован")

    async def generate(self, request: ContentRequest) -> GeneratedContent:
        """
        Сгенерировать контент

        Args:
            request: Параметры генерации

        Returns:
            Сгенерированный контент
        """
        logger.info(f"📝 Генерация {request.content_type.value} для {request.product_name}")

        if request.content_type == ContentType.SALES_COPY:
            return await self._generate_sales_copy(request)
        elif request.content_type == ContentType.BLOG_ARTICLE:
            return await self._generate_blog_article(request)
        elif request.content_type == ContentType.SOCIAL_POST:
            return await self._generate_social_post(request)
        elif request.content_type == ContentType.EMAIL:
            return await self._generate_email(request)
        elif request.content_type == ContentType.LANDING_PAGE:
            return await self._generate_landing_page(request)
        elif request.content_type == ContentType.AD_CREATIVE:
            return await self._generate_ad_creative(request)
        else:
            raise ValueError(f"Unsupported content type: {request.content_type}")

    async def _generate_sales_copy(self, request: ContentRequest) -> GeneratedContent:
        """Генерация продающего текста"""

        lang = request.language
        structure = self.SALES_COPY_STRUCTURE[lang]

        # Заголовок
        headline_template = random.choice(self.SALES_HEADLINES[lang])
        headline = headline_template.format(
            product=request.product_name,
            usp=request.unique_selling_points[0] if request.unique_selling_points else "инновационное решение",
            benefit="достичь результата",
            number=len(request.unique_selling_points),
            category="своей области",
            audience=request.target_audience.split(',')[0] if ',' in request.target_audience else request.target_audience
        )

        # Тело продающего текста
        pain_points = {
            "ru": ["неэффективных процессов", "потери времени", "низких результатов"],
            "en": ["inefficient processes", "wasted time", "low results"]
        }

        problem = structure["problem"].format(
            pain_point=random.choice(pain_points[lang])
        )

        solution = structure["solution"].format(
            product=request.product_name,
            solution_description=request.product_description
        )

        # Список преимуществ
        benefits_list = "\n".join(f"✓ {usp}" for usp in request.unique_selling_points)

        benefits = structure["benefits"].format(
            product=request.product_name,
            benefits_list=benefits_list
        )

        social_proof = structure["social_proof"].format(
            number=random.choice(["1000", "5000", "10000"]),
            product=request.product_name
        )

        # CTA
        cta_text = random.choice(self.CALL_TO_ACTIONS[lang])
        cta = structure["cta"].format(
            cta=cta_text,
            benefit="получите результат" if lang == "ru" else "get results"
        )

        # Собрать всё вместе
        content = f"""
{headline}

{problem}

{solution}

{benefits}

{social_proof}

{cta}
        """.strip()

        # Хэштеги из keywords
        hashtags = [kw.replace(" ", "") for kw in request.keywords[:5]]

        return GeneratedContent(
            content=content,
            headline=headline,
            call_to_action=cta_text,
            hashtags=hashtags,
            seo_metadata=self._generate_seo_metadata(request),
            variants=[content]  # TODO: Генерировать A/B варианты
        )

    async def _generate_blog_article(self, request: ContentRequest) -> GeneratedContent:
        """Генерация SEO-статьи для блога"""

        lang = request.language

        # Заголовок статьи (H1)
        title_templates = {
            "ru": [
                "Полное руководство по {topic}",
                "Как {action}: пошаговое руководство",
                "{topic}: всё, что нужно знать в {year}",
                "{number} лучших способов {action}",
            ],
            "en": [
                "Complete guide to {topic}",
                "How to {action}: step-by-step guide",
                "{topic}: everything you need to know in {year}",
                "{number} best ways to {action}",
            ]
        }

        from datetime import datetime
        year = datetime.now().year

        headline = random.choice(title_templates[lang]).format(
            topic=request.product_name,
            action="использовать " + request.product_name if lang == "ru" else f"use {request.product_name}",
            year=year,
            number=random.choice([5, 7, 10])
        )

        # Структура статьи
        intro = f"""
{request.product_description}

В этой статье мы подробно разберём, как {request.product_name} помогает {request.target_audience} достигать своих целей.
        """.strip() if lang == "ru" else f"""
{request.product_description}

In this article, we'll explore how {request.product_name} helps {request.target_audience} achieve their goals.
        """.strip()

        # Секции с USP
        sections = []
        for i, usp in enumerate(request.unique_selling_points, 1):
            section_title = f"## {i}. {usp}"
            section_body = f"""
{usp} - одно из ключевых преимуществ {request.product_name}. Это позволяет пользователям экономить время и повышать эффективность.
            """.strip() if lang == "ru" else f"""
{usp} is one of the key advantages of {request.product_name}. This allows users to save time and increase efficiency.
            """.strip()

            sections.append(f"{section_title}\n\n{section_body}")

        sections_text = "\n\n".join(sections)

        # Заключение
        conclusion = f"""
## Заключение

{request.product_name} - мощное решение для {request.target_audience}. Попробуйте сегодня и убедитесь сами!
        """.strip() if lang == "ru" else f"""
## Conclusion

{request.product_name} is a powerful solution for {request.target_audience}. Try it today and see for yourself!
        """.strip()

        # Собрать статью
        article = f"""
# {headline}

{intro}

{sections_text}

{conclusion}
        """.strip()

        # SEO-оптимизация
        seo_metadata = self._generate_seo_metadata(request)
        seo_metadata["word_count"] = str(len(article.split()))
        seo_metadata["reading_time"] = str(len(article.split()) // 200) + " мин"

        return GeneratedContent(
            content=article,
            headline=headline,
            call_to_action="Попробовать сейчас" if lang == "ru" else "Try now",
            hashtags=[kw.replace(" ", "") for kw in request.keywords],
            seo_metadata=seo_metadata
        )

    async def _generate_social_post(self, request: ContentRequest) -> GeneratedContent:
        """Генерация поста для соцсетей"""

        platform = request.platform
        lang = request.language

        # Адаптация под платформу
        if platform == Platform.TWITTER:
            max_length = 280
        elif platform == Platform.LINKEDIN:
            max_length = 1300
        elif platform == Platform.FACEBOOK:
            max_length = 500
        elif platform == Platform.INSTAGRAM:
            max_length = 2200
        else:
            max_length = 500

        # Шаблоны постов
        post_templates = {
            "ru": [
                "🚀 {product} - {usp}\n\n{description}\n\n{cta}",
                "✨ {hook}\n\n{product} помогает {audience}:\n{benefits}\n\n{cta}",
                "💡 Знаете ли вы?\n\n{fact}\n\nС {product} это реальность!\n\n{cta}",
            ],
            "en": [
                "🚀 {product} - {usp}\n\n{description}\n\n{cta}",
                "✨ {hook}\n\n{product} helps {audience}:\n{benefits}\n\n{cta}",
                "💡 Did you know?\n\n{fact}\n\nWith {product} it's reality!\n\n{cta}",
            ]
        }

        template = random.choice(post_templates[lang])

        # Короткий список benefits для соцсетей
        benefits_short = "\n".join(f"✓ {usp[:50]}" for usp in request.unique_selling_points[:3])

        post = template.format(
            product=request.product_name,
            usp=request.unique_selling_points[0] if request.unique_selling_points else "",
            description=request.product_description[:150],
            audience=request.target_audience,
            benefits=benefits_short,
            cta=random.choice(self.CALL_TO_ACTIONS[lang]),
            hook="Представьте себе:" if lang == "ru" else "Imagine:",
            fact=f"{request.product_name} уже используют тысячи человек" if lang == "ru" else f"Thousands already use {request.product_name}"
        )

        # Обрезка под лимит платформы
        if len(post) > max_length:
            post = post[:max_length-3] + "..."

        # Хэштеги
        hashtags = [kw.replace(" ", "").replace("-", "") for kw in request.keywords[:5]]

        # Добавить хэштеги в конец (если влезают)
        hashtag_string = " ".join(f"#{tag}" for tag in hashtags)
        if len(post) + len(hashtag_string) + 2 <= max_length:
            post += "\n\n" + hashtag_string

        return GeneratedContent(
            content=post,
            headline=request.product_name,
            call_to_action=random.choice(self.CALL_TO_ACTIONS[lang]),
            hashtags=hashtags
        )

    async def _generate_email(self, request: ContentRequest) -> GeneratedContent:
        """Генерация email-рассылки"""

        lang = request.language

        # Subject line (заголовок письма)
        subject_templates = {
            "ru": [
                "{product} - специальное предложение внутри",
                "Как {product} изменит вашу работу",
                "Эксклюзивно для вас: {product}",
                "{number} причин попробовать {product}",
            ],
            "en": [
                "{product} - special offer inside",
                "How {product} will change your work",
                "Exclusive for you: {product}",
                "{number} reasons to try {product}",
            ]
        }

        subject = random.choice(subject_templates[lang]).format(
            product=request.product_name,
            number=len(request.unique_selling_points)
        )

        # Тело письма
        email_body = f"""
Здравствуйте!

{request.product_description}

Вот что делает {request.product_name} особенным:

{chr(10).join(f'• {usp}' for usp in request.unique_selling_points)}

Специально для вас мы подготовили эксклюзивное предложение.

{random.choice(self.CALL_TO_ACTIONS[lang])} →

С уважением,
Команда {request.product_name}
        """.strip() if lang == "ru" else f"""
Hello!

{request.product_description}

Here's what makes {request.product_name} special:

{chr(10).join(f'• {usp}' for usp in request.unique_selling_points)}

We've prepared an exclusive offer just for you.

{random.choice(self.CALL_TO_ACTIONS[lang])} →

Best regards,
{request.product_name} Team
        """.strip()

        return GeneratedContent(
            content=email_body,
            headline=subject,
            call_to_action=random.choice(self.CALL_TO_ACTIONS[lang])
        )

    async def _generate_landing_page(self, request: ContentRequest) -> GeneratedContent:
        """Генерация текста для Landing Page"""

        lang = request.language

        # Hero section
        hero_headline = f"{request.product_name} - {request.unique_selling_points[0]}" if request.unique_selling_points else request.product_name
        hero_subheadline = request.product_description

        # Features section
        features = "\n\n".join(
            f"### {usp}\n{request.product_description[:100]}"
            for usp in request.unique_selling_points
        )

        # CTA section
        cta_headline = "Готовы начать?" if lang == "ru" else "Ready to start?"
        cta_button = random.choice(self.CALL_TO_ACTIONS[lang])

        landing_page = f"""
# {hero_headline}

## {hero_subheadline}

{cta_button}

---

## Преимущества

{features}

---

## {cta_headline}

{request.product_name} поможет вам достичь ваших целей.

{cta_button}
        """.strip()

        return GeneratedContent(
            content=landing_page,
            headline=hero_headline,
            call_to_action=cta_button,
            seo_metadata=self._generate_seo_metadata(request)
        )

    async def _generate_ad_creative(self, request: ContentRequest) -> GeneratedContent:
        """Генерация рекламного креатива"""

        lang = request.language

        # Короткий, цепляющий текст
        ad_templates = {
            "ru": [
                "{hook}\n\n{product} - {usp}\n\n{cta} →",
                "{product}\n{usp}\n\nТолько сегодня: {offer}\n{cta}",
                "Как {audience} {benefit}?\n\n{product}!\n\n{cta}",
            ],
            "en": [
                "{hook}\n\n{product} - {usp}\n\n{cta} →",
                "{product}\n{usp}\n\nToday only: {offer}\n{cta}",
                "How {audience} {benefit}?\n\n{product}!\n\n{cta}",
            ]
        }

        ad_text = random.choice(ad_templates[lang]).format(
            hook="🎯 Внимание!" if lang == "ru" else "🎯 Attention!",
            product=request.product_name,
            usp=request.unique_selling_points[0] if request.unique_selling_points else "",
            cta=random.choice(self.CALL_TO_ACTIONS[lang]),
            audience=request.target_audience,
            benefit="повышают эффективность" if lang == "ru" else "increase efficiency",
            offer="-20%" if lang == "ru" else "-20%"
        )

        return GeneratedContent(
            content=ad_text,
            headline=request.product_name,
            call_to_action=random.choice(self.CALL_TO_ACTIONS[lang]),
            hashtags=[kw.replace(" ", "") for kw in request.keywords[:3]]
        )

    def _generate_seo_metadata(self, request: ContentRequest) -> Dict[str, str]:
        """Генерация SEO метаданных"""

        # Meta description
        meta_description = f"{request.product_description[:150]}..." if len(request.product_description) > 150 else request.product_description

        # Meta keywords
        meta_keywords = ", ".join(request.keywords)

        # OG tags
        og_title = f"{request.product_name} - {request.unique_selling_points[0]}" if request.unique_selling_points else request.product_name
        og_description = meta_description

        return {
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "og_title": og_title,
            "og_description": og_description,
            "og_type": "product"
        }

    async def generate_ab_variants(self, request: ContentRequest, count: int = 3) -> List[GeneratedContent]:
        """
        Генерировать несколько вариантов для A/B тестирования

        Args:
            request: Параметры контента
            count: Количество вариантов

        Returns:
            Список сгенерированных вариантов
        """
        logger.info(f"🔬 Генерация {count} A/B вариантов")

        variants = []
        for i in range(count):
            variant = await self.generate(request)
            variants.append(variant)

        return variants


# === ДЕМО ===
if __name__ == "__main__":
    import asyncio

    print("✍️ Демо: Marketing Content Generator")
    print("=" * 80)

    generator = MarketingContentGenerator()

    async def demo():
        # Запрос на генерацию продающего текста
        request = ContentRequest(
            content_type=ContentType.SALES_COPY,
            product_name="TaskMaster Pro",
            product_description="Умный планировщик задач с AI-ассистентом",
            target_audience="Занятые профессионалы, фрилансеры, студенты",
            unique_selling_points=[
                "AI-планирование с учётом приоритетов",
                "Автоматическое распределение задач",
                "Интеграция с 50+ сервисами",
                "Геймификация и мотивация",
            ],
            keywords=["продуктивность", "планирование", "AI", "тайм-менеджмент"],
            tone=ToneOfVoice.ENTHUSIASTIC,
            language="ru"
        )

        # Генерация продающего текста
        print("\n📝 Генерация продающего текста...")
        sales_copy = await generator.generate(request)
        print(f"\n{sales_copy.content}")
        print(f"\n📊 Хэштеги: {', '.join('#' + h for h in sales_copy.hashtags)}")

        # Генерация поста для Twitter
        print("\n" + "=" * 80)
        print("\n📱 Генерация поста для Twitter...")
        request.content_type = ContentType.SOCIAL_POST
        request.platform = Platform.TWITTER
        twitter_post = await generator.generate(request)
        print(f"\n{twitter_post.content}")

        # Генерация статьи для блога
        print("\n" + "=" * 80)
        print("\n📰 Генерация статьи для блога...")
        request.content_type = ContentType.BLOG_ARTICLE
        article = await generator.generate(request)
        print(f"\n{article.content[:500]}...")
        print(f"\n📊 SEO: {article.seo_metadata}")

    asyncio.run(demo())

    print("\n✅ Демо завершено!")
