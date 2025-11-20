#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TRADING BOT AI - Configuration
Все настройки в одном месте
"""

import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TELEGRAM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3-turbo"

# Голос (мультиязычный из Оракула)
VOICE = "en-US-AvaMultilingualNeural"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA SOURCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEWSDATA_API_KEY = os.getenv('NEWSDATA_API_KEY')
FRED_API_KEY = os.getenv('FRED_API_KEY')
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

# API endpoints (бесплатные)
BINANCE_API = "https://api.binance.com/api/v3"
COINGECKO_API = "https://api.coingecko.com/api/v3"
WHALE_ALERT_API = "https://api.whale-alert.io/v1"
FEAR_GREED_API = "https://api.alternative.me/fng"
FOREX_API = "https://api.forexrateapi.com/v1"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRADING SYMBOLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Крипта (топ-10 по капитализации)
CRYPTO_SYMBOLS = [
    "BTC", "ETH", "SOL", "BNB", "XRP",
    "ADA", "DOGE", "MATIC", "AVAX", "DOT"
]

# Форекс (major pairs)
FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY",
    "AUD/USD", "USD/CHF", "USD/CAD"
]

# Commodities (сырьё)
COMMODITIES = [
    "XAU/USD",  # Gold
    "XAG/USD",  # Silver
    "BRENT",    # Oil
    "NATGAS",   # Natural Gas
    "COPPER"    # Copper
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANALYSIS PARAMETERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Минимальный объём транзакции кита (в USD)
WHALE_MIN_VALUE = 1_000_000

# Таймфреймы для анализа
TIMEFRAMES = ["1h", "4h", "1d"]

# Вес каждого агента в финальном решении
AGENT_WEIGHTS = {
    "technical": 0.25,      # Технический анализ
    "smart_money": 0.30,    # Smart Money (киты)
    "sentiment": 0.20,      # Sentiment
    "macro": 0.15,          # Макро
    "resonance": 0.10       # Резонанс методов
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# THRESHOLDS (Пороги для сигналов)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Уровень уверенности для сигнала
CONFIDENCE_BUY = 0.75   # BUY если >= 75%
CONFIDENCE_SELL = 0.75  # SELL если >= 75%
CONFIDENCE_HOLD = 0.60  # HOLD если 60-75%

# RSI пороги
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Fear & Greed Index
FG_EXTREME_FEAR = 25    # Extreme Fear (покупать!)
FG_EXTREME_GREED = 75   # Extreme Greed (продавать!)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import logging

logging.basicConfig(
    level=logging.INFO,
    filename="trading_bot.log",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VALIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def validate_config():
    """Проверка что все ключи на месте"""
    required = {
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        "GROQ_API_KEY": GROQ_API_KEY,
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        logger.error(f"❌ Отсутствуют ключи: {', '.join(missing)}")
        raise ValueError(f"Missing API keys: {', '.join(missing)}")

    logger.info("✅ Все ключи загружены")

# Проверяем при импорте
validate_config()
