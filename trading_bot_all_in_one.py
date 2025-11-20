#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TRADING BOT AI - ВСЁ В ОДНОМ ФАЙЛЕ
Просто запусти: python trading_bot_all_in_one.py
"""

import asyncio
import logging
import httpx
import edge_tts
import os
import io
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# НАСТРОЙКИ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_telegram_token_here")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
GROQ_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3-turbo"
VOICE = "en-US-AvaMultilingualNeural"

BINANCE_API = "https://api.binance.com/api/v3"
COINGECKO_API = "https://api.coingecko.com/api/v3"

CRYPTO_SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "MATIC", "AVAX", "DOT"]
FOREX_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF", "USD/CAD"]
COMMODITIES = ["XAU/USD", "XAG/USD", "BRENT", "NATGAS", "COPPER"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ГОЛОСОВАЯ СИСТЕМА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_language(text: str) -> str:
    try:
        russian_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        total_chars = len([c for c in text if c.isalpha()])
        if total_chars == 0:
            return 'ru'
        return 'ru' if (russian_chars / total_chars) > 0.3 else 'en'
    except:
        return 'ru'

async def transcribe_voice(file_path: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        with open(file_path, "rb") as f:
            audio_data = f.read()
        audio_file = io.BytesIO(audio_data)
        audio_file.name = os.path.basename(file_path)
        files = {"file": (audio_file.name, audio_file, "audio/ogg")}
        data = {"model": WHISPER_MODEL, "response_format": "json", "temperature": 0.0}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers, files=files, data=data
            )
            response.raise_for_status()
            result = response.json()
        return result.get("text", "")
    except Exception as e:
        logger.error(f"❌ Ошибка распознавания: {e}")
        return ""

async def text_to_speech(text: str, output_file: str) -> bool:
    try:
        clean_text = text
        for emoji in ["📊", "🔮", "✨", "🌟", "🎯", "**", "*", "_", "📈", "📉", "🟢", "🔴", "⚠️", "💰", "🐋", "📰"]:
            clean_text = clean_text.replace(emoji, "")
        communicate = edge_tts.Communicate(clean_text, VOICE)
        await communicate.save(output_file)
        return os.path.exists(output_file) and os.path.getsize(output_file) > 0
    except Exception as e:
        logger.error(f"❌ Ошибка TTS: {e}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ДАННЫЕ КРИПТЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_crypto_price(symbol: str) -> Optional[Dict]:
    try:
        pair = f"{symbol}USDT"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BINANCE_API}/ticker/24hr", params={"symbol": pair})
            response.raise_for_status()
            data = response.json()
        return {
            "symbol": symbol,
            "price": float(data["lastPrice"]),
            "change_24h": float(data["priceChangePercent"]),
            "volume_24h": float(data["volume"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
        }
    except Exception as e:
        logger.error(f"❌ Ошибка получения цены {symbol}: {e}")
        return None

async def get_fear_greed_index() -> Optional[Dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.alternative.me/fng/")
            response.raise_for_status()
            data = response.json()
        fng = data["data"][0]
        return {"value": int(fng["value"]), "classification": fng["value_classification"]}
    except Exception as e:
        logger.error(f"❌ Ошибка Fear & Greed: {e}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI АГЕНТЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def analyze_technical(symbol: str, price_data: Dict) -> Dict:
    change_24h = price_data.get("change_24h", 0)
    if change_24h < -10:
        rsi_score = 0.8
    elif change_24h > 10:
        rsi_score = 0.2
    else:
        rsi_score = 0.5

    volume = price_data.get("volume_24h", 0)
    change = price_data.get("change_24h", 0)
    if volume > 1_000_000 and change > 0:
        volume_score = 0.75
    elif volume > 1_000_000 and change < 0:
        volume_score = 0.25
    else:
        volume_score = 0.5

    final_score = (rsi_score * 0.5 + volume_score * 0.5)
    direction = "BUY" if final_score >= 0.65 else ("SELL" if final_score <= 0.35 else "HOLD")

    return {
        "agent": "technical",
        "symbol": symbol,
        "score": final_score,
        "direction": direction,
        "confidence": final_score if final_score >= 0.5 else (1 - final_score)
    }

async def analyze_smart_money(symbol: str, price_data: Dict) -> Dict:
    change_24h = price_data.get("change_24h", 0)
    volume = price_data.get("volume_24h", 0)

    if change_24h > 3 and volume > 500_000:
        score = 0.8
    elif change_24h < -3 and volume > 500_000:
        score = 0.2
    else:
        score = 0.5

    direction = "BUY" if score >= 0.65 else ("SELL" if score <= 0.35 else "HOLD")

    return {
        "agent": "smart_money",
        "symbol": symbol,
        "score": score,
        "direction": direction,
        "confidence": score if score >= 0.5 else (1 - score)
    }

async def analyze_sentiment(symbol: str, price_data: Dict, fg_data: Optional[Dict]) -> Dict:
    if fg_data:
        value = fg_data.get("value", 50)
        if value <= 25:
            fg_score = 0.85
        elif value <= 45:
            fg_score = 0.65
        elif value >= 75:
            fg_score = 0.15
        elif value >= 55:
            fg_score = 0.35
        else:
            fg_score = 0.5
    else:
        fg_score = 0.5

    direction = "BUY" if fg_score >= 0.65 else ("SELL" if fg_score <= 0.35 else "HOLD")

    return {
        "agent": "sentiment",
        "symbol": symbol,
        "score": fg_score,
        "direction": direction,
        "confidence": fg_score if fg_score >= 0.5 else (1 - fg_score)
    }

async def synthesize_decision(symbol: str, agent_results: List[Dict], price_data: Dict, language: str = 'ru') -> Dict:
    # Взвешенный score
    scores = [r.get("score", 0.5) for r in agent_results]
    weighted_score = sum(scores) / len(scores)

    # Резонанс
    directions = [r.get("direction") for r in agent_results]
    buy_count = directions.count("BUY")
    sell_count = directions.count("SELL")

    # AI анализ через Groq
    try:
        system_prompt = """Ты эксперт-трейдер. Проанализируй данные и дай краткий анализ (150 слов):

📊 СИГНАЛ: [BUY/SELL/HOLD]
💪 УВЕРЕННОСТЬ: [X%]

📈 ТЕХНИЧЕСКИЙ АНАЛИЗ: [2-3 предложения]
🐋 SMART MONEY: [2-3 предложения]
💬 SENTIMENT: [2-3 предложения]
🎯 РЕКОМЕНДАЦИЯ: [3-4 предложения]
⚠️ РИСКИ: [1-2 предложения]

БЕЗ ЭМОДЗИ В ТЕКСТЕ!"""

        user_message = f"""Актив: {symbol}
Цена: ${price_data.get('price', 0):.2f}
Изменение 24ч: {price_data.get('change_24h', 0):+.2f}%

СИГНАЛЫ:
- Technical: {agent_results[0]['direction']}
- Smart Money: {agent_results[1]['direction']}
- Sentiment: {agent_results[2]['direction']}"""

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=data
            )
            response.raise_for_status()
            result = response.json()

        ai_analysis = result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"❌ Ошибка AI: {e}")
        ai_analysis = "Ошибка AI анализа"

    final_direction = "BUY" if buy_count >= 2 else ("SELL" if sell_count >= 2 else "HOLD")

    return {
        "symbol": symbol,
        "direction": final_direction,
        "confidence": weighted_score,
        "ai_analysis": ai_analysis,
        "agent_results": agent_results
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TELEGRAM BOT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("📊 Анализ крипты"), KeyboardButton("💱 Форекс")],
        [KeyboardButton("⚡ Commodities"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """🤖 **TRADING BOT AI**

📊 Анализ крипты (BTC, ETH, SOL...)
🗣️ Голосовое управление!

Выбери в меню 👇""",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📊 Анализ крипты":
        keyboard = []
        for i in range(0, len(CRYPTO_SYMBOLS), 2):
            row = [InlineKeyboardButton(s, callback_data=f"crypto_{s}") for s in CRYPTO_SYMBOLS[i:i+2]]
            keyboard.append(row)
        await update.message.reply_text("📊 **Выбери:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def analyze_asset(symbol: str, update: Update, language: str = 'ru'):
    status_msg = await update.effective_message.reply_text(f"🔮 Анализирую {symbol}...\n⏳ 15-20 секунд...")

    try:
        # Получаем данные
        price_data = await get_crypto_price(symbol)
        fg_data = await get_fear_greed_index()

        if not price_data:
            await status_msg.edit_text(f"❌ Нет данных для {symbol}")
            return

        # Агенты
        agent_results = await asyncio.gather(
            analyze_technical(symbol, price_data),
            analyze_smart_money(symbol, price_data),
            analyze_sentiment(symbol, price_data, fg_data)
        )

        # Meta Agent
        final_decision = await synthesize_decision(symbol, agent_results, price_data, language)
        response_text = final_decision.get("ai_analysis", "")

        # Голос
        audio_path = f"analysis_{int(datetime.now().timestamp())}.mp3"
        audio_success = await text_to_speech(response_text, audio_path)

        await status_msg.delete()

        # Отправляем голос
        if audio_success and os.path.exists(audio_path):
            with open(audio_path, 'rb') as audio:
                await update.effective_message.reply_audio(
                    audio=audio,
                    title=f"{symbol} Analysis",
                    caption=f"🗣️ **Анализ {symbol}**",
                    parse_mode="Markdown"
                )
            os.remove(audio_path)

        # Текст
        await update.effective_message.reply_text(response_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        await status_msg.edit_text(f"❌ Ошибка анализа {symbol}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("crypto_"):
        symbol = query.data.replace("crypto_", "")
        await analyze_asset(symbol, update)

def main():
    print("🤖 TRADING BOT AI - STARTING")
    print("📊 Crypto + AI + Voice")
    print("=" * 60)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(📊 Анализ крипты)$'), handle_menu_buttons))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("✅ Бот запущен! Напиши /start\n")
    app.run_polling(allowed_updates=None)

if __name__ == "__main__":
    main()
