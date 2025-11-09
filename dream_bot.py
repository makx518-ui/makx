#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import httpx
import edge_tts
import os
import io
import json
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
    ContextTypes,
)

# Загружаем переменные из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv не установлен. Установи: pip install python-dotenv")
    print("⚠️ Используй переменные окружения напрямую.")

# ========== НАСТРОЙКИ ==========
# Получаем из переменных окружения (БЕЗОПАСНО!)
# ВАЖНО: Создай файл .env и укажи там свои ключи!
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3-turbo"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_PAYMENT_TOKEN = os.getenv("TELEGRAM_PAYMENT_TOKEN", "")  # Для Telegram Stars или провайдера

# Монетизация
DEMO_MODE = True  # ДЕМО до конца ноября
DEMO_END_DATE = datetime(2025, 11, 30, 23, 59, 59)

PRICE_INTERPRETATION = 250  # рублей за трактовку
PRICE_VIDEO = 250  # рублей за видео
PRICE_BUNDLE = 500  # рублей за трактовку + видео
PRICE_SUBSCRIPTION = 12000  # рублей за месяц безлимита

# HeyGen API
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "")
HEYGEN_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID", "")
HEYGEN_VOICE_ID = os.getenv("HEYGEN_VOICE_ID", "")
HEYGEN_ENABLED = bool(HEYGEN_API_KEY)

# Тестовое видео
TEST_VIDEO_MODE = True
TEST_VIDEO_PATH = os.path.join(os.getcwd(), "demo_video.mp4")

MAX_REPLY_LENGTH = 4000
VOICE = "ru-RU-DmitryNeural"  # Русский голос для TTS

# Папки
DATA_DIR = "data/dreams"
DB_FILE = "data/users.db"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename="dream_bot.log",
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

# ========== БАЗА ДАННЫХ ==========
def init_database():
    """Инициализация базы данных пользователей"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'ru',
            subscription_until TIMESTAMP,
            interpretations_count INTEGER DEFAULT 0,
            videos_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            payment_type TEXT,
            amount INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()
    logger.info("✅ База данных инициализирована")

def get_or_create_user(user_id: int, username: str = None, first_name: str = None) -> dict:
    """Получить или создать пользователя"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

    conn.close()

    return {
        'user_id': user[0],
        'username': user[1],
        'first_name': user[2],
        'language': user[3],
        'subscription_until': user[4],
        'interpretations_count': user[5],
        'videos_count': user[6],
        'created_at': user[7]
    }

def has_active_subscription(user_id: int) -> bool:
    """Проверка активной подписки"""
    if DEMO_MODE and datetime.now() < DEMO_END_DATE:
        return True  # Демо-режим - все бесплатно!

    user = get_or_create_user(user_id)
    if user['subscription_until']:
        sub_date = datetime.fromisoformat(user['subscription_until'])
        return sub_date > datetime.now()
    return False

def add_subscription(user_id: int, months: int = 1):
    """Добавить подписку"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    user = get_or_create_user(user_id)

    if user['subscription_until']:
        current_end = datetime.fromisoformat(user['subscription_until'])
        if current_end > datetime.now():
            new_end = current_end + timedelta(days=30 * months)
        else:
            new_end = datetime.now() + timedelta(days=30 * months)
    else:
        new_end = datetime.now() + timedelta(days=30 * months)

    cursor.execute("""
        UPDATE users SET subscription_until = ? WHERE user_id = ?
    """, (new_end.isoformat(), user_id))

    conn.commit()
    conn.close()

    logger.info(f"✅ Подписка добавлена для {user_id} до {new_end}")

def increment_usage(user_id: int, usage_type: str):
    """Увеличить счетчик использования"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if usage_type == 'interpretation':
        cursor.execute("""
            UPDATE users SET interpretations_count = interpretations_count + 1
            WHERE user_id = ?
        """, (user_id,))
    elif usage_type == 'video':
        cursor.execute("""
            UPDATE users SET videos_count = videos_count + 1
            WHERE user_id = ?
        """, (user_id,))

    conn.commit()
    conn.close()

# ========== ОПРЕДЕЛЕНИЕ ЯЗЫКА ==========
def detect_language(text: str) -> str:
    """Определяет язык текста (ru или en)"""
    try:
        russian_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        total_chars = len([c for c in text if c.isalpha()])

        if total_chars == 0:
            return 'ru'

        russian_ratio = russian_chars / total_chars
        return 'ru' if russian_ratio > 0.3 else 'en'
    except:
        return 'ru'

# ========== ПРОМПТЫ ДЛЯ РАЗНЫХ ЯЗЫКОВ ==========
SYSTEM_PROMPT_RU = """
Ты — Оракул Снов. Мудрый толкователь снов, который говорит простым и понятным языком.

Когда пользователь описывает сон, дай структурированную трактовку:

💬 ПРОСТОЕ ТОЛКОВАНИЕ (средний абзац)
Объясни сон простыми словами, как бы ты рассказывал другу. Что означает этот сон в жизни человека.

📚 ПСИХОЛОГИЧЕСКИЙ СМЫСЛ (по Фрейду) (4-5 строк)
Какие скрытые желания, потребности или страхи отражает этот сон.

✨ ЭЗОТЕРИЧЕСКАЯ ТРАКТОВКА (2 средних абзаца)
Духовное значение, энергетика, кармические уроки, символы Таро.

🌟 ФИЛОСОФСКИЙ ВЗГЛЯД (4-5 строк)
Как этот сон связан с выбором, свободой, смыслом жизни.

🎯 ЧТО ДЕЛАТЬ (4-5 строк)
Практические советы, медитации, аффирмации.

ВАЖНО:
- Пиши тепло, по-человечески
- НЕ ПОВТОРЯЙСЯ
- Общий объём: 1500-1800 символов
- НЕ используй эмодзи в тексте (они плохо озвучиваются!)
"""

SYSTEM_PROMPT_EN = """
You are the Dream Oracle. A wise dream interpreter who speaks in simple, clear language.

When a user describes a dream, provide a structured interpretation:

💬 SIMPLE INTERPRETATION (medium paragraph)
Explain the dream in simple words, as you would tell a friend.

📚 PSYCHOLOGICAL MEANING (Freudian) (4-5 lines)
What hidden desires, needs or fears does this dream reflect.

✨ ESOTERIC INTERPRETATION (2 medium paragraphs)
Spiritual meaning, energy, karmic lessons, Tarot symbols.

🌟 PHILOSOPHICAL VIEW (4-5 lines)
How this dream relates to choice, freedom, meaning of life.

🎯 WHAT TO DO (4-5 lines)
Practical advice, meditations, affirmations.

IMPORTANT:
- Write warmly, humanly
- DO NOT REPEAT
- Total volume: 1500-1800 characters
- DO NOT use emojis in text (they sound bad when voiced!)
"""

# ========== ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ ==========
def get_welcome_text() -> str:
    """Получить приветственное сообщение с учетом ДЕМО режима"""
    demo_notice = ""
    if DEMO_MODE and datetime.now() < DEMO_END_DATE:
        days_left = (DEMO_END_DATE - datetime.now()).days
        demo_notice = f"""
🎉 БЕСПЛАТНАЯ ДЕМО-ВЕРСИЯ до 30 ноября!
🎉 FREE DEMO VERSION until November 30th!
⏰ Осталось дней / Days left: {days_left}

ВСЕ ФУНКЦИИ БЕСПЛАТНО! / ALL FEATURES FREE!
"""

    return f"""
🌙 Добро пожаловать в Оракул Снов!
🌙 Welcome to Dream Oracle!

{demo_notice}
🌍 Мультиязычный / Multilingual: 🇷🇺 Русский • 🇬🇧 English

Я помогу тебе раскрыть тайны подсознания через анализ снов.
I will help you unlock the secrets of your subconscious.

Что я умею / What I can do:
🔮 Глубокий психоанализ / Deep psychoanalysis
✨ Эзотерическая трактовка / Esoteric interpretation
🗣️ Голосовая трактовка / Voice interpretation
🎨 AI-изображение сна / AI dream image
🎬 Видео с AI-аватаром / AI avatar video

Готов начать? / Ready to start? 👇
"""

# ========== ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ ==========
async def generate_image_prompt(dream_text: str, language: str) -> str:
    """Создаёт английский промпт для изображения"""
    try:
        logger.info("🎨 Создаю промпт для изображения...")

        system_prompt = """Create a detailed, artistic prompt in English for generating a dreamlike image.
Focus on: surreal atmosphere, key visual symbols, colors and mood, artistic style.
Keep it concise (50-100 words) but vivid. ONLY English prompt!"""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        user_prompt = f"Dream: {dream_text}" if language == 'en' else f"Сон: {dream_text}"

        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 200,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()

        prompt = result["choices"][0]["message"]["content"].strip()
        logger.info(f"✅ Промпт создан: {prompt[:100]}...")
        return prompt

    except Exception as e:
        logger.error(f"❌ Ошибка создания промпта: {e}")
        return None

async def generate_dream_image(prompt: str, output_file: str, retry_count: int = 3) -> bool:
    """Генерирует изображение через Pollinations.ai (БЕСПЛАТНО!)"""
    for attempt in range(retry_count):
        try:
            logger.info(f"🎨 Попытка {attempt + 1}/{retry_count}: Генерирую изображение...")

            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)

            API_URL = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&enhance=true&nologo=true"

            async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                response = await client.get(API_URL)

                if response.status_code != 200:
                    if attempt == retry_count - 1:
                        return False
                    await asyncio.sleep(5)
                    continue

                with open(output_file, 'wb') as f:
                    f.write(response.content)

                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    logger.info(f"✅ Изображение успешно создано!")
                    return True

        except Exception as e:
            logger.error(f"❌ Ошибка генерации (попытка {attempt + 1}): {e}")
            if attempt == retry_count - 1:
                return False
            await asyncio.sleep(5)

    return False

# ========== ГОЛОСОВЫЕ ФУНКЦИИ ==========
async def transcribe_voice(file_path: str) -> str:
    """Распознавание голоса через Groq Whisper"""
    try:
        logger.info(f"🎤 Распознаю голос: {file_path}")

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

        with open(file_path, "rb") as audio_file:
            files = {"file": (os.path.basename(file_path), audio_file, "audio/ogg")}
            data = {
                "model": WHISPER_MODEL,
                "response_format": "json",
                "temperature": 0.0,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data
                )
                response.raise_for_status()
                result = response.json()

        transcription = result.get("text", "")
        logger.info(f"✅ Распознано: {transcription[:100]}...")
        return transcription

    except Exception as e:
        logger.error(f"❌ Ошибка распознавания: {e}")
        return ""

async def text_to_speech(text: str, output_file: str, language: str = 'ru') -> bool:
    """Озвучивание текста через Edge TTS"""
    try:
        logger.info(f"🗣️ Создаю голосовое сообщение...")

        # Убираем эмодзи и спецсимволы
        clean_text = text.replace("📚", "").replace("🔮", "").replace("✨", "")
        clean_text = clean_text.replace("🌟", "").replace("🎯", "").replace("**", "")
        clean_text = clean_text.replace("*", "").replace("_", "")

        # Выбираем голос
        voice = "ru-RU-DmitryNeural" if language == 'ru' else "en-US-AriaNeural"

        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(output_file)

        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            logger.info(f"✅ Аудио создано: {output_file}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"❌ Ошибка TTS: {e}")
        return False

# ========== GROQ API ==========
async def query_groq_api(user_message: str, language: str) -> str:
    """Запрос к Groq API для анализа сна"""
    try:
        logger.info(f"🔮 Анализирую сон (язык: {language})")

        system_prompt = SYSTEM_PROMPT_RU if language == 'ru' else SYSTEM_PROMPT_EN

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.8,
            "max_tokens": 2000,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()

        full_response = result["choices"][0]["message"]["content"]
        logger.info(f"✅ Трактовка получена ({len(full_response)} символов)")

        return full_response

    except Exception as e:
        logger.error(f"❌ Ошибка Groq API: {e}")
        return None

# ========== TELEGRAM HANDLERS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    user_id = update.effective_user.user_id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    # Создаём/получаем пользователя
    get_or_create_user(user_id, username, first_name)

    # Проверяем подписку
    has_sub = has_active_subscription(user_id)

    # Кнопки главного меню
    keyboard = [
        [InlineKeyboardButton("🔮 Рассказать сон / Tell a dream", callback_data="tell_dream")],
        [InlineKeyboardButton("💎 Тарифы / Pricing", callback_data="pricing")],
        [InlineKeyboardButton("📊 Мой профиль / My profile", callback_data="profile")],
        [InlineKeyboardButton("ℹ️ Помощь / Help", callback_data="help")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        get_welcome_text(),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    logger.info(f"✅ Пользователь {user_id} ({first_name}) запустил бота")

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок меню"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    callback_data = query.data

    if callback_data == "tell_dream":
        await tell_dream_menu(update, context)

    elif callback_data == "pricing":
        await show_pricing(update, context)

    elif callback_data == "profile":
        await show_profile(update, context)

    elif callback_data == "help":
        await show_help(update, context)

    elif callback_data == "main_menu":
        await show_main_menu(update, context)

async def tell_dream_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню рассказа сна"""
    query = update.callback_query
    user_id = query.from_user.id

    has_sub = has_active_subscription(user_id)

    if DEMO_MODE and datetime.now() < DEMO_END_DATE:
        status = "🎉 ДЕМО - ВСЕ БЕСПЛАТНО!"
    elif has_sub:
        status = "✅ У вас есть подписка!"
    else:
        status = f"💰 Трактовка: {PRICE_INTERPRETATION}₽ | Видео: {PRICE_VIDEO}₽"

    message = f"""🌌 Оракул готов слушать / Oracle is ready

{status}

Расскажи свой сон:
📝 Напиши текстом / Write in text
🎤 Запиши голосом / Record by voice

✨ Чем подробнее - тем глубже трактовка!
✨ More detailed - deeper interpretation!"""

    keyboard = [
        [InlineKeyboardButton("◀️ Главное меню / Main menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(message, reply_markup=reply_markup)
    context.user_data['waiting_for_dream'] = True

async def show_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать тарифы"""
    query = update.callback_query
    user_id = query.from_user.id

    if DEMO_MODE and datetime.now() < DEMO_END_DATE:
        days_left = (DEMO_END_DATE - datetime.now()).days

        message = f"""🎉 БЕСПЛАТНАЯ ДЕМО-ВЕРСИЯ!
🎉 FREE DEMO VERSION!

⏰ Действует до / Valid until: 30 ноября 2025
⏰ Осталось дней / Days left: {days_left}

✨ ВСЕ функции доступны БЕСПЛАТНО!
✨ ALL features available for FREE!

После окончания демо-периода:
After demo period ends:

💎 Тарифы / Pricing:

1️⃣ Трактовка сна / Dream interpretation
   💰 {PRICE_INTERPRETATION}₽
   🔮 Психологический анализ
   ✨ Эзотерическая трактовка
   🗣️ Голосовое сообщение
   🎨 AI-изображение

2️⃣ Видео с AI-аватаром / AI avatar video
   💰 {PRICE_VIDEO}₽
   🎬 Профессиональное видео
   🤖 HeyGen AI технология

3️⃣ Комплект / Bundle (трактовка + видео)
   💰 {PRICE_BUNDLE}₽ (экономия 50₽!)

4️⃣ Подписка на месяц / Monthly subscription
   💰 {PRICE_SUBSCRIPTION}₽
   ♾️ Безлимитные трактовки
   ♾️ Безлимитные видео
   ⭐ VIP поддержка

Успей воспользоваться ДЕМО! 🎁
Enjoy the DEMO while it lasts! 🎁"""
    else:
        message = f"""💎 Тарифы Оракула Снов / Dream Oracle Pricing

1️⃣ Трактовка сна / Dream interpretation
   💰 {PRICE_INTERPRETATION}₽
   🔮 Психологический анализ (Фрейд)
   ✨ Эзотерическая трактовка
   🗣️ Голосовое сообщение
   🎨 AI-изображение сна

2️⃣ Видео с AI-аватаром / AI avatar video
   💰 {PRICE_VIDEO}₽
   🎬 Профессиональное видео
   🤖 HeyGen AI технология

3️⃣ Комплект / Bundle
   💰 {PRICE_BUNDLE}₽ (экономия 50₽!)
   🎁 Трактовка + Видео

4️⃣ Подписка на месяц / Monthly subscription
   💰 {PRICE_SUBSCRIPTION}₽
   ♾️ Безлимитные трактовки
   ♾️ Безлимитные видео
   ⭐ VIP поддержка
   💫 Приоритетная обработка"""

    keyboard = [
        [InlineKeyboardButton("💳 Купить подписку / Buy subscription", callback_data="buy_subscription")],
        [InlineKeyboardButton("◀️ Главное меню / Main menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать профиль пользователя"""
    query = update.callback_query
    user_id = query.from_user.id

    user = get_or_create_user(user_id)
    has_sub = has_active_subscription(user_id)

    if DEMO_MODE and datetime.now() < DEMO_END_DATE:
        sub_status = "🎉 ДЕМО-версия (все бесплатно до 30.11.2025)"
    elif has_sub:
        sub_date = datetime.fromisoformat(user['subscription_until'])
        days_left = (sub_date - datetime.now()).days
        sub_status = f"✅ Подписка активна до {sub_date.strftime('%d.%m.%Y')} ({days_left} дней)"
    else:
        sub_status = "❌ Подписка не активна"

    message = f"""👤 Профиль / Profile

👤 Имя / Name: {user['first_name']}
🆔 ID: {user['user_id']}
🌍 Язык / Language: {user['language'].upper()}

{sub_status}

📊 Статистика / Statistics:
🔮 Трактовок / Interpretations: {user['interpretations_count']}
🎬 Видео / Videos: {user['videos_count']}
📅 Регистрация / Registered: {user['created_at'][:10]}"""

    keyboard = [
        [InlineKeyboardButton("◀️ Главное меню / Main menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать помощь"""
    query = update.callback_query

    message = """ℹ️ Помощь / Help

Как пользоваться ботом:

1️⃣ Нажми "Рассказать сон"
2️⃣ Опиши свой сон текстом или голосом
3️⃣ Получи глубокую трактовку + изображение
4️⃣ Создай видео с AI-аватаром (опционально)

🌍 Бот понимает русский и английский
🎤 Можно использовать голосовые сообщения
🎨 AI создаст изображение твоего сна
🎬 AI-аватар расскажет трактовку на видео

💡 Советы:
- Описывай сон как можно подробнее
- Укажи свои эмоции во сне
- Вспомни важные детали и символы

📧 Поддержка / Support: @your_support

How to use the bot:

1️⃣ Click "Tell a dream"
2️⃣ Describe your dream in text or voice
3️⃣ Get deep interpretation + image
4️⃣ Create video with AI avatar (optional)

🌍 Bot understands Russian and English
🎤 Voice messages supported
🎨 AI will create your dream image
🎬 AI avatar will tell interpretation on video"""

    keyboard = [
        [InlineKeyboardButton("◀️ Главное меню / Main menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать главное меню"""
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("🔮 Рассказать сон / Tell a dream", callback_data="tell_dream")],
        [InlineKeyboardButton("💎 Тарифы / Pricing", callback_data="pricing")],
        [InlineKeyboardButton("📊 Мой профиль / My profile", callback_data="profile")],
        [InlineKeyboardButton("ℹ️ Помощь / Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(get_welcome_text(), reply_markup=reply_markup, parse_mode="Markdown")

async def process_dream(dream_text: str, update: Update, context: ContextTypes.DEFAULT_TYPE, processing_msg):
    """Обработка сна - главная функция"""
    user_id = update.effective_user.id
    language = detect_language(dream_text)

    # Проверка подписки (если не ДЕМО)
    has_sub = has_active_subscription(user_id)

    if not has_sub and not (DEMO_MODE and datetime.now() < DEMO_END_DATE):
        # Нужна оплата
        await processing_msg.edit_text(
            "💰 Для получения трактовки необходима оплата.\n"
            "Выбери вариант:\n\n"
            f"1️⃣ Трактовка: {PRICE_INTERPRETATION}₽\n"
            f"2️⃣ Комплект (трактовка + видео): {PRICE_BUNDLE}₽\n"
            f"3️⃣ Подписка на месяц: {PRICE_SUBSCRIPTION}₽",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"💳 Оплатить {PRICE_INTERPRETATION}₽", callback_data="pay_interpretation")],
                [InlineKeyboardButton(f"💳 Оплатить {PRICE_BUNDLE}₽", callback_data="pay_bundle")],
                [InlineKeyboardButton(f"💳 Подписка {PRICE_SUBSCRIPTION}₽", callback_data="buy_subscription")]
            ])
        )
        context.user_data['pending_dream'] = dream_text
        return

    # Получаем трактовку
    response = await query_groq_api(dream_text, language)

    if not response:
        await processing_msg.edit_text("❌ Произошла ошибка. Попробуй ещё раз!")
        return

    # Сохраняем для видео
    context.user_data['last_dream_text'] = dream_text
    context.user_data['last_interpretation'] = response

    # Увеличиваем счетчик
    increment_usage(user_id, 'interpretation')

    # Генерируем изображение
    status_msg = "🎨 Создаю AI-изображение...\n⏳ 15-20 секунд..."
    if language == 'en':
        status_msg = "🎨 Creating AI image...\n⏳ 15-20 seconds..."

    await processing_msg.edit_text(status_msg)

    image_path = f"dream_{update.effective_message.message_id}.png"
    image_success = False

    image_prompt = await generate_image_prompt(dream_text, language)
    if image_prompt:
        image_success = await generate_dream_image(image_prompt, image_path)

    # Создаём голос
    status_msg = "🗣️ Создаю голосовую трактовку...\n⏳ 10-15 секунд..."
    if language == 'en':
        status_msg = "🗣️ Creating voice...\n⏳ 10-15 seconds..."

    await processing_msg.edit_text(status_msg)

    audio_path = f"response_{update.effective_message.message_id}.mp3"
    audio_success = await text_to_speech(response, audio_path, language)

    try:
        await processing_msg.delete()
    except:
        pass

    # Отправляем результаты

    # 1. Изображение
    if image_success and os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as img:
                await update.effective_message.reply_photo(
                    photo=img,
                    caption="🎨 AI-визуализация сна / AI dream visualization"
                )
        except Exception as e:
            logger.error(f"❌ Ошибка отправки изображения: {e}")

    # 2. Кнопка для видео
    keyboard = [[InlineKeyboardButton("🎬 Создать видео / Create video", callback_data="create_video")]]
    if not has_sub and not (DEMO_MODE and datetime.now() < DEMO_END_DATE):
        keyboard[0][0] = InlineKeyboardButton(f"🎬 Видео ({PRICE_VIDEO}₽)", callback_data="pay_video")

    keyboard.append([InlineKeyboardButton("◀️ Главное меню / Main menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        "✨ Твоя трактовка готова! / Your interpretation is ready!\n\n"
        "👇 Нажми для видео / Click for video",
        reply_markup=reply_markup
    )

    # 3. Голос
    if audio_success:
        try:
            with open(audio_path, 'rb') as audio:
                await update.effective_message.reply_audio(
                    audio=audio,
                    title="Dream Interpretation",
                    performer="Dream Oracle",
                    caption="🗣️ Голосовая трактовка / Voice interpretation"
                )
            os.remove(audio_path)
        except Exception as e:
            logger.error(f"❌ Ошибка отправки аудио: {e}")

    # 4. Текст
    await update.effective_message.reply_text(
        f"📜 Текстовая версия:\n\n{response}",
        parse_mode="Markdown"
    )

    # Очистка
    context.user_data['waiting_for_dream'] = False

    if image_success and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except:
            pass

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    if not context.user_data.get('waiting_for_dream'):
        await update.message.reply_text("Сначала нажми 'Рассказать сон' в меню!")
        return

    processing_msg = await update.message.reply_text("🎤 Слушаю...\n⏳ 5-10 секунд...")

    try:
        voice_file = await update.message.voice.get_file()
        voice_path = f"voice_{update.message.voice.file_id}.ogg"
        await voice_file.download_to_drive(voice_path)

        transcribed_text = await transcribe_voice(voice_path)

        if not transcribed_text:
            await processing_msg.edit_text("❌ Не удалось распознать")
            return

        await processing_msg.edit_text(f"✅ Услышал:\n\n{transcribed_text[:200]}...\n\n🔮 Анализирую...")
        await asyncio.sleep(2)

        await process_dream(transcribed_text, update, context, processing_msg)

        try:
            os.remove(voice_path)
        except:
            pass

    except Exception as e:
        logger.error(f"❌ Ошибка обработки голоса: {e}")
        await processing_msg.edit_text("❌ Ошибка")

async def handle_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (описание сна)"""
    if not context.user_data.get('waiting_for_dream'):
        await update.message.reply_text(
            "Сначала нажми 'Рассказать сон' в меню!\n"
            "First click 'Tell a dream' in menu!"
        )
        return

    user_input = update.message.text

    processing_msg = await update.message.reply_text(
        "🔮 Оракул анализирует...\n⏳ 20-30 секунд..."
    )

    await process_dream(user_input, update, context, processing_msg)

async def create_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание видео"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Проверка доступа
    has_sub = has_active_subscription(user_id)

    if not has_sub and not (DEMO_MODE and datetime.now() < DEMO_END_DATE):
        await query.message.reply_text(
            f"💰 Для создания видео нужна оплата: {PRICE_VIDEO}₽\n"
            "Или оформи подписку для безлимита!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"💳 Оплатить {PRICE_VIDEO}₽", callback_data="pay_video")],
                [InlineKeyboardButton(f"💳 Подписка {PRICE_SUBSCRIPTION}₽", callback_data="buy_subscription")]
            ])
        )
        return

    # ДЕМО режим - показываем тестовое видео
    if TEST_VIDEO_MODE and os.path.exists(TEST_VIDEO_PATH):
        processing_msg = await query.message.reply_text(
            "🎬 Загружаю ДЕМО видео...\n"
            "💡 Это пример того, как будет выглядеть твоё видео!"
        )

        try:
            with open(TEST_VIDEO_PATH, 'rb') as video:
                await query.message.reply_video(
                    video=video,
                    caption="🎬 ДЕМО: AI-аватар рассказывает сон!\n\n"
                            "🤖 HeyGen AI Technology\n"
                            "💡 Когда активируем HeyGen, аватар будет рассказывать ТВОЮ трактовку!",
                    supports_streaming=True
                )

            await processing_msg.delete()
            increment_usage(user_id, 'video')
            logger.info("✅ Тестовое видео отправлено!")
            return

        except Exception as e:
            logger.error(f"❌ Ошибка отправки видео: {e}")
            await processing_msg.delete()
            return

    # Если HeyGen не активен
    if not HEYGEN_ENABLED:
        await query.message.reply_text(
            "⚠️ Видео с AI-аватаром временно недоступно\n\n"
            "💡 Функция будет активирована после подключения HeyGen!\n"
            "⏳ Следи за обновлениями!"
        )
        return

    # Здесь будет код для реального HeyGen
    await query.message.reply_text("🎬 Функция в разработке!")

def main():
    """Запуск бота"""
    print("=" * 60)
    print("🌙 ЗАПУСК ОРАКУЛ СНОВ / LAUNCHING DREAM ORACLE")
    print("=" * 60)

    # Проверка обязательных ключей
    if not GROQ_API_KEY:
        print("❌ ОШИБКА: GROQ_API_KEY не указан!")
        print("💡 Создай файл .env и укажи GROQ_API_KEY=your_key")
        print("💡 Или установи переменную окружения: export GROQ_API_KEY=your_key")
        return

    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не указан!")
        print("💡 Создай файл .env и укажи TELEGRAM_TOKEN=your_token")
        print("💡 Или установи переменную окружения: export TELEGRAM_TOKEN=your_token")
        return

    # Инициализация БД
    init_database()

    print(f"🤖 Groq Model: {GROQ_MODEL}")
    print(f"🎤 Whisper Model: {WHISPER_MODEL}")
    print(f"🗣️ TTS Voice: {VOICE}")

    if DEMO_MODE and datetime.now() < DEMO_END_DATE:
        days_left = (DEMO_END_DATE - datetime.now()).days
        print(f"🎉 ДЕМО РЕЖИМ АКТИВЕН! Осталось {days_left} дней до 30.11.2025")
        print("✅ Все функции БЕСПЛАТНЫ!")
    else:
        print(f"💰 Монетизация активна:")
        print(f"   - Трактовка: {PRICE_INTERPRETATION}₽")
        print(f"   - Видео: {PRICE_VIDEO}₽")
        print(f"   - Подписка: {PRICE_SUBSCRIPTION}₽/месяц")

    if TEST_VIDEO_MODE:
        print(f"🎬 Тестовое видео: {TEST_VIDEO_PATH}")
    elif HEYGEN_ENABLED:
        print(f"🎬 HeyGen: ✅ ВКЛЮЧЕНО")
    else:
        print(f"🎬 HeyGen: ⚠️ ОТКЛЮЧЕНО")

    print("🎨 Images: Pollinations.ai (FLUX)")
    print("💾 Database: SQLite")
    print("=" * 60)

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .read_timeout(120)
        .write_timeout(120)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dream))

    print("\n✅ Бот запущен!")
    print("📱 Напиши /start своему боту")
    print("\nДля остановки нажми Ctrl+C\n")

    app.run_polling(allowed_updates=None)

if __name__ == "__main__":
    main()
