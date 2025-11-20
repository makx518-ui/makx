#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 TECHNICAL AGENT - Технический анализ
RSI, MACD, Volume, Support/Resistance
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ТЕХНИЧЕСКИЙ АНАЛИЗ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_rsi_signal(price_data: Dict) -> float:
    """Сигнал на основе RSI (0-1)"""
    try:
        # Упрощённый RSI на основе изменения цены за 24ч
        change_24h = price_data.get("change_24h", 0)

        if change_24h < -10:  # Сильное падение
            rsi_score = 0.8  # Oversold - вероятно отскок (BUY)
        elif change_24h < -5:
            rsi_score = 0.65
        elif change_24h > 10:  # Сильный рост
            rsi_score = 0.2  # Overbought - вероятно коррекция (SELL)
        elif change_24h > 5:
            rsi_score = 0.35
        else:
            rsi_score = 0.5  # Нейтрально

        logger.info(f"📈 RSI сигнал: {rsi_score:.2f} (change: {change_24h:+.2f}%)")
        return rsi_score

    except Exception as e:
        logger.error(f"❌ Ошибка RSI: {e}")
        return 0.5

def calculate_volume_signal(price_data: Dict) -> float:
    """Сигнал на основе объёма (0-1)"""
    try:
        volume = price_data.get("volume_24h", 0)
        change = price_data.get("change_24h", 0)

        # Большой объём + рост = сильный BUY
        if volume > 1_000_000 and change > 0:
            return 0.75
        # Большой объём + падение = сильный SELL
        elif volume > 1_000_000 and change < 0:
            return 0.25
        else:
            return 0.5

    except Exception as e:
        logger.error(f"❌ Ошибка Volume: {e}")
        return 0.5

def calculate_price_action_signal(price_data: Dict) -> float:
    """Сигнал на основе price action (0-1)"""
    try:
        price = price_data.get("price", 0)
        high_24h = price_data.get("high_24h", price)
        low_24h = price_data.get("low_24h", price)

        # Если цена близка к максимуму 24ч
        if high_24h > 0:
            position = (price - low_24h) / (high_24h - low_24h) if high_24h != low_24h else 0.5

            if position > 0.9:  # Цена у верхней границы
                return 0.3  # Вероятна коррекция
            elif position < 0.1:  # Цена у нижней границы
                return 0.7  # Вероятен отскок
            else:
                return 0.5

        return 0.5

    except Exception as e:
        logger.error(f"❌ Ошибка Price Action: {e}")
        return 0.5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ГЛАВНАЯ ФУНКЦИЯ ТЕХНИЧЕСКОГО АГЕНТА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def analyze_technical(symbol: str, price_data: Dict) -> Dict:
    """Технический анализ актива"""
    logger.info(f"📊 Technical Agent анализирует {symbol}...")

    rsi_signal = calculate_rsi_signal(price_data)
    volume_signal = calculate_volume_signal(price_data)
    price_action_signal = calculate_price_action_signal(price_data)

    # Средневзвешенный сигнал
    final_score = (rsi_signal * 0.4 + volume_signal * 0.3 + price_action_signal * 0.3)

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
        "agent": "technical",
        "symbol": symbol,
        "score": final_score,
        "direction": direction,
        "confidence": confidence,
        "signals": {
            "rsi": rsi_signal,
            "volume": volume_signal,
            "price_action": price_action_signal
        }
    }

    logger.info(f"✅ Technical: {direction} (confidence: {confidence:.2%})")
    return result
