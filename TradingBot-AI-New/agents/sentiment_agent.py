#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💬 SENTIMENT AGENT - Анализ настроения рынка
Fear & Greed Index + News
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SENTIMENT ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_fear_greed(fg_data: Optional[Dict]) -> float:
    """Анализ Fear & Greed Index (0-1)"""
    try:
        if not fg_data:
            return 0.5

        value = fg_data.get("value", 50)
        classification = fg_data.get("classification", "Neutral")

        logger.info(f"😱 Fear & Greed: {value}/100 ({classification})")

        # CONTRARIAN подход:
        # Extreme Fear (0-25) = BUY opportunity!
        # Extreme Greed (75-100) = SELL warning!

        if value <= 25:  # Extreme Fear
            logger.info("🔥 EXTREME FEAR - Возможность покупки!")
            return 0.85  # Сильный BUY сигнал
        elif value <= 45:  # Fear
            return 0.65  # Умеренный BUY
        elif value >= 75:  # Extreme Greed
            logger.warning("⚠️ EXTREME GREED - Риск коррекции!")
            return 0.15  # Сильный SELL сигнал
        elif value >= 55:  # Greed
            return 0.35  # Умеренный SELL
        else:  # Neutral (46-54)
            return 0.5

    except Exception as e:
        logger.error(f"❌ Ошибка F&G анализа: {e}")
        return 0.5

def analyze_market_momentum(price_data: Dict) -> float:
    """Анализ импульса рынка (0-1)"""
    try:
        change_24h = price_data.get("change_24h", 0)

        # Сильный импульс вверх
        if change_24h > 10:
            return 0.75
        elif change_24h > 5:
            return 0.65
        # Сильный импульс вниз
        elif change_24h < -10:
            return 0.25
        elif change_24h < -5:
            return 0.35
        else:
            return 0.5

    except Exception as e:
        logger.error(f"❌ Ошибка momentum: {e}")
        return 0.5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ГЛАВНАЯ ФУНКЦИЯ SENTIMENT АГЕНТА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def analyze_sentiment(symbol: str, price_data: Dict, fg_data: Optional[Dict] = None) -> Dict:
    """Анализ настроения рынка"""
    logger.info(f"💬 Sentiment Agent анализирует {symbol}...")

    fg_signal = analyze_fear_greed(fg_data)
    momentum_signal = analyze_market_momentum(price_data)

    # Средневзвешенный сигнал
    final_score = (fg_signal * 0.7 + momentum_signal * 0.3)

    # Определяем направление
    if final_score >= 0.65:
        direction = "BUY"
        confidence = final_score
    elif final_score <= 0.35:
        direction = "SELL"
        confidence = 1 - final_score
    else:
        direction = "HOLD"
        confidence = 0.5

    result = {
        "agent": "sentiment",
        "symbol": symbol,
        "score": final_score,
        "direction": direction,
        "confidence": confidence,
        "signals": {
            "fear_greed": fg_signal,
            "momentum": momentum_signal
        }
    }

    logger.info(f"✅ Sentiment: {direction} (confidence: {confidence:.2%})")
    return result
