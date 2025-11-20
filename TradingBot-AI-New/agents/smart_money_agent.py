#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐋 SMART MONEY AGENT - Отслеживание умных денег
Киты, топ-трейдеры, exchange flows
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SMART MONEY ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_whale_activity(market_data: Dict) -> float:
    """Анализ активности китов (0-1)"""
    try:
        # На основе market cap и volume
        market_cap = market_data.get("market_cap", 0)
        volume = market_data.get("total_volume", 0)

        if market_cap > 0:
            volume_to_mcap_ratio = volume / market_cap

            # Высокое отношение объёма к капитализации
            # = активность китов
            if volume_to_mcap_ratio > 0.2:
                logger.info(f"🐋 Высокая активность китов! ({volume_to_mcap_ratio:.2%})")
                return 0.75  # Киты активны - вероятен сильный импульс
            elif volume_to_mcap_ratio > 0.1:
                return 0.6
            else:
                return 0.5

        return 0.5

    except Exception as e:
        logger.error(f"❌ Ошибка анализа китов: {e}")
        return 0.5

def analyze_accumulation_distribution(price_data: Dict, market_data: Dict) -> float:
    """Накопление или распределение (0-1)"""
    try:
        change_24h = price_data.get("change_24h", 0)
        volume = price_data.get("volume_24h", 0)

        # Рост цены + высокий объём = накопление (BUY)
        if change_24h > 3 and volume > 500_000:
            logger.info("📈 Фаза накопления (киты покупают)")
            return 0.8
        # Падение цены + высокий объём = распределение (SELL)
        elif change_24h < -3 and volume > 500_000:
            logger.info("📉 Фаза распределения (киты продают)")
            return 0.2
        else:
            return 0.5

    except Exception as e:
        logger.error(f"❌ Ошибка A/D: {e}")
        return 0.5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ГЛАВНАЯ ФУНКЦИЯ SMART MONEY АГЕНТА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def analyze_smart_money(symbol: str, price_data: Dict, market_data: Dict) -> Dict:
    """Анализ умных денег"""
    logger.info(f"🐋 Smart Money Agent анализирует {symbol}...")

    whale_signal = analyze_whale_activity(market_data)
    accum_dist_signal = analyze_accumulation_distribution(price_data, market_data)

    # Средневзвешенный сигнал
    final_score = (whale_signal * 0.6 + accum_dist_signal * 0.4)

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
        "agent": "smart_money",
        "symbol": symbol,
        "score": final_score,
        "direction": direction,
        "confidence": confidence,
        "signals": {
            "whale_activity": whale_signal,
            "accumulation": accum_dist_signal
        }
    }

    logger.info(f"✅ Smart Money: {direction} (confidence: {confidence:.2%})")
    return result
