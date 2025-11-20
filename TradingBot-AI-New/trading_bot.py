#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TRADING BOT AI - Main Bot
Супер код с нуля на основе лучших практик из Оракула
"""

import asyncio
import logging
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# Импорты наших модулей
from config import TELEGRAM_TOKEN, CRYPTO_SYMBOLS, FOREX_PAIRS, COMMODITIES
from voice.voice_system import transcribe_voice, text_to_speech, detect_language

# Data sources
from data_sources.crypto_data import get_full_crypto_data, get_fear_greed_index
from data_sources.forex_data import get_forex_rate, get_commodity_price

# AI Agents
from agents.technical_agent import analyze_technical
from agents.smart_money_agent import analyze_smart_money
from agents.sentiment_agent import analyze_sentiment
from agents.meta_agent import synthesize_decision

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# МЕНЮ И ИНТЕРФЕЙС
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Постоянное меню (из Оракула)"""
    keyboard = [
        [KeyboardButton("📊 Анализ крипты"), KeyboardButton("💱 Форекс")],
        [KeyboardButton("⚡ Commodities"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_welcome_text() -> str:
    """Приветствие"""
    return """🤖 **TRADING BOT AI - Супер аналитика!**

🌍 **Мультиязычный / Multilingual: RU • EN**

**Что я умею:**
📊 Анализ крипты (BTC, ETH, SOL...)
💱 Форекс (EUR/USD, GBP/USD...)
⚡ Commodities (Золото, Нефть, Газ)

🗣️ **Голосовое управление!**
🎤 Скажи "Проанализируй биткоин"
🔊 Получи ответ голосом!

**Выбери в меню** 👇
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# КОМАНДЫ БОТА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    logger.info(f"✅ Пользователь {user_id} ({first_name}) запустил бота")

    await update.message.reply_text(
        get_welcome_text(),
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    help_text = """ℹ️ **ПОМОЩЬ / HELP**

**Как пользоваться:**

1️⃣ Выбери актив из меню
2️⃣ Или напиши голосом/текстом
3️⃣ Получи AI-анализ + голосовой ответ

**Примеры запросов:**
• "Проанализируй Bitcoin"
• "Analyze BTC"
• "EUR/USD прогноз"
• "Золото куда пойдёт?"

**Поддерживаемые активы:**
📊 Крипта: BTC, ETH, SOL, BNB, XRP...
💱 Форекс: EUR/USD, GBP/USD...
⚡ Сырьё: XAU/USD (золото), Brent (нефть)

🗣️ **Голосовое управление работает!**
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ОБРАБОТКА КНОПОК МЕНЮ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок меню"""
    text = update.message.text

    if text == "📊 Анализ крипты":
        # Показываем топ-крипту
        keyboard = []
        for i in range(0, len(CRYPTO_SYMBOLS), 2):
            row = []
            for symbol in CRYPTO_SYMBOLS[i:i+2]:
                row.append(InlineKeyboardButton(symbol, callback_data=f"crypto_{symbol}"))
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📊 **Выбери криптовалюту:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif text == "💱 Форекс":
        keyboard = []
        for pair in FOREX_PAIRS:
            keyboard.append([InlineKeyboardButton(pair, callback_data=f"forex_{pair}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "💱 **Выбери валютную пару:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif text == "⚡ Commodities":
        keyboard = []
        for commodity in COMMODITIES:
            keyboard.append([InlineKeyboardButton(commodity, callback_data=f"commodity_{commodity}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚡ **Выбери сырьё:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif text == "ℹ️ Помощь":
        await help_command(update, context)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ГЛАВНАЯ ФУНКЦИЯ АНАЛИЗА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def analyze_asset(symbol: str, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str = 'ru'):
    """Главная функция анализа актива"""
    user_id = update.effective_user.id
    logger.info(f"🔍 Анализирую {symbol} для user {user_id}")

    # Статусное сообщение
    status_msg = await update.effective_message.reply_text(
        f"🔮 Анализирую {symbol}...\n⏳ 15-20 секунд..."
    )

    try:
        # 1. Получаем данные
        await status_msg.edit_text(f"📊 Собираю данные {symbol}...")

        crypto_data = await get_full_crypto_data(symbol)
        price_data = crypto_data.get("price", {})
        market_data = crypto_data.get("market", {})
        fg_data = await get_fear_greed_index()

        if not price_data:
            await status_msg.edit_text(f"❌ Не удалось получить данные для {symbol}")
            return

        # 2. Запускаем агентов параллельно
        await status_msg.edit_text(f"🤖 Запускаю AI агентов...")

        agent_results = await asyncio.gather(
            analyze_technical(symbol, price_data),
            analyze_smart_money(symbol, price_data, market_data),
            analyze_sentiment(symbol, price_data, fg_data)
        )

        # 3. Meta Agent - финальное решение
        await status_msg.edit_text(f"🧠 AI синтезирует решение...")

        final_decision = await synthesize_decision(
            symbol, agent_results, price_data, language
        )

        # 4. Формируем ответ
        await status_msg.edit_text(f"✍️ Создаю отчёт...")

        response_text = final_decision.get("ai_analysis", "")

        # 5. Создаём голосовое сообщение
        await status_msg.edit_text(f"🗣️ Создаю голосовой ответ...")

        audio_path = f"analysis_{user_id}_{int(datetime.now().timestamp())}.mp3"
        audio_success = await text_to_speech(response_text, audio_path)

        # 6. Удаляем статусное сообщение
        try:
            await status_msg.delete()
        except:
            pass

        # 7. Отправляем голосовой ответ
        if audio_success and os.path.exists(audio_path):
            try:
                with open(audio_path, 'rb') as audio:
                    await update.effective_message.reply_audio(
                        audio=audio,
                        title=f"{symbol} Analysis",
                        performer="Trading Bot AI",
                        caption=f"🗣️ **Голосовой анализ {symbol}**",
                        parse_mode="Markdown"
                    )

                # Удаляем аудио
                os.remove(audio_path)
            except Exception as e:
                logger.error(f"❌ Ошибка отправки аудио: {e}")

        # 8. Отправляем текстовую версию
        await update.effective_message.reply_text(
            response_text,
            parse_mode="Markdown"
        )

        # 9. Кнопка "Анализировать ещё"
        keyboard = [[InlineKeyboardButton("🔄 Анализировать ещё", callback_data="show_crypto_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_message.reply_text(
            "✨ Хочешь ещё? / Want more? 👇",
            reply_markup=reply_markup
        )

        logger.info(f"✅ Анализ {symbol} завершён для user {user_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка анализа {symbol}: {e}")
        import traceback
        logger.error(traceback.format_exc())

        await status_msg.edit_text(
            f"❌ Произошла ошибка при анализе {symbol}\nПопробуй ещё раз!"
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CALLBACK ОБРАБОТЧИКИ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка inline кнопок"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("crypto_"):
        symbol = data.replace("crypto_", "")
        await analyze_asset(symbol, update, context)

    elif data.startswith("forex_"):
        pair = data.replace("forex_", "")
        # TODO: Реализовать анализ форекс
        await query.message.reply_text(f"📊 Форекс анализ {pair} (в разработке)")

    elif data.startswith("commodity_"):
        commodity = data.replace("commodity_", "")
        # TODO: Реализовать анализ commodities
        await query.message.reply_text(f"⚡ Анализ {commodity} (в разработке)")

    elif data == "show_crypto_menu":
        # Показываем меню крипты снова
        keyboard = []
        for i in range(0, len(CRYPTO_SYMBOLS), 2):
            row = []
            for symbol in CRYPTO_SYMBOLS[i:i+2]:
                row.append(InlineKeyboardButton(symbol, callback_data=f"crypto_{symbol}"))
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "📊 **Выбери криптовалюту:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ГОЛОСОВЫЕ СООБЩЕНИЯ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    processing_msg = await update.message.reply_text(
        "🎤 Слушаю... / Listening...\n⏳ 5-10 секунд..."
    )

    try:
        voice_file = await update.message.voice.get_file()
        voice_path = f"voice_{update.message.voice.file_id}.ogg"
        await voice_file.download_to_drive(voice_path)

        # Распознаём
        transcribed_text = await transcribe_voice(voice_path)

        # Удаляем голосовой файл
        try:
            os.remove(voice_path)
        except:
            pass

        if not transcribed_text:
            await processing_msg.edit_text("❌ Не удалось распознать")
            return

        language = detect_language(transcribed_text)

        await processing_msg.edit_text(
            f"✅ Услышал:\n_{transcribed_text}_\n\n🔮 Анализирую...",
            parse_mode="Markdown"
        )

        # TODO: Определить что пользователь хочет проанализировать
        # Пока просто отправляем назад
        await processing_msg.edit_text(
            f"✅ Распознал: {transcribed_text}\n\nИспользуй меню для выбора актива!"
        )

    except Exception as e:
        logger.error(f"❌ Ошибка обработки голоса: {e}")
        await processing_msg.edit_text("❌ Ошибка обработки голоса")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ЗАПУСК БОТА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("=" * 60)
    print("🤖 TRADING BOT AI - LAUNCHING")
    print("=" * 60)
    print("📊 Assets: Crypto + Forex + Commodities")
    print("🤖 AI Agents: 3 (Technical, Smart Money, Sentiment)")
    print("🧠 Meta Agent: Groq Llama 3.3 70B")
    print("🗣️ Voice: Edge TTS (Multilingual)")
    print("🌍 Languages: RU + EN")
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

    # Обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Обработчики кнопок меню
    menu_filter = filters.TEXT & filters.Regex('^(📊 Анализ крипты|💱 Форекс|⚡ Commodities|ℹ️ Помощь)$')
    app.add_handler(MessageHandler(menu_filter, handle_menu_buttons))

    # Callback кнопки
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Голосовые сообщения
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("\n✅ Бот запущен! / Bot started!")
    print("📱 Напиши /start боту / Write /start to bot")
    print("🎛️ Используй меню / Use menu")
    print("🎤 Голос работает / Voice enabled")
    print("\nCtrl+C для остановки / to stop\n")

    app.run_polling(allowed_updates=None)

if __name__ == "__main__":
    main()
