#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 META AGENT - Синтез всех сигналов
Финальное решение через AI (Groq Llama 3.3)
"""

import logging
import httpx
from typing import Dict, List
from config import GROQ_API_KEY, GROQ_MODEL, AGENT_WEIGHTS

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WEIGHTED SCORE CALCULATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_weighted_score(agent_results: List[Dict]) -> float:
    """Средневзвешенный score от всех агентов"""
    total_score = 0.0
    total_weight = 0.0

    for result in agent_results:
        agent_name = result.get("agent")
        score = result.get("score", 0.5)
        weight = AGENT_WEIGHTS.get(agent_name, 0.2)

        total_score += score * weight
        total_weight += weight

    if total_weight > 0:
        return total_score / total_weight
    return 0.5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESONANCE DETECTION (Резонанс методов)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_resonance(agent_results: List[Dict]) -> Dict:
    """Детекция резонанса между методами"""
    directions = [r.get("direction") for r in agent_results]

    buy_count = directions.count("BUY")
    sell_count = directions.count("SELL")
    hold_count = directions.count("HOLD")

    total = len(directions)

    # Сильный резонанс = 75%+ агентов согласны
    if buy_count / total >= 0.75:
        resonance = "STRONG_BUY"
        strength = buy_count / total
    elif sell_count / total >= 0.75:
        resonance = "STRONG_SELL"
        strength = sell_count / total
    # Умеренный резонанс = 60%+ согласны
    elif buy_count / total >= 0.6:
        resonance = "MODERATE_BUY"
        strength = buy_count / total
    elif sell_count / total >= 0.6:
        resonance = "MODERATE_SELL"
        strength = sell_count / total
    else:
        resonance = "NO_CONSENSUS"
        strength = 0.5

    logger.info(f"🔄 Резонанс: {resonance} (strength: {strength:.2%})")

    return {
        "type": resonance,
        "strength": strength,
        "buy_votes": buy_count,
        "sell_votes": sell_count,
        "hold_votes": hold_count
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI-POWERED FINAL DECISION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_ai_final_decision(
    symbol: str,
    agent_results: List[Dict],
    resonance: Dict,
    price_data: Dict,
    language: str = 'ru'
) -> str:
    """Финальное решение через Groq AI"""
    try:
        logger.info("🧠 Запрашиваю финальное решение у AI...")

        # Формируем промпт
        if language == 'ru':
            system_prompt = """Ты — эксперт-трейдер с 15+ годами опыта.

Проанализируй данные от агентов и дай краткий анализ (150-200 слов):

СТРУКТУРА ОТВЕТА:
📊 СИГНАЛ: [BUY/SELL/HOLD]
💪 УВЕРЕННОСТЬ: [X%]

📈 ТЕХНИЧЕСКИЙ АНАЛИЗ:
[2-3 предложения]

🐋 SMART MONEY:
[2-3 предложения]

💬 SENTIMENT:
[2-3 предложения]

🎯 РЕКОМЕНДАЦИЯ:
[3-4 предложения с конкретным советом]

⚠️ РИСКИ:
[1-2 предложения]

БЕЗ ЭМОДЗИ В ТЕКСТЕ! Только в заголовках."""

            user_message = f"""Актив: {symbol}
Цена: ${price_data.get('price', 0):.2f}
Изменение 24ч: {price_data.get('change_24h', 0):+.2f}%

СИГНАЛЫ АГЕНТОВ:
"""
        else:
            system_prompt = """You are an expert trader with 15+ years of experience.

Analyze agent data and give brief analysis (150-200 words):

STRUCTURE:
📊 SIGNAL: [BUY/SELL/HOLD]
💪 CONFIDENCE: [X%]

📈 TECHNICAL ANALYSIS:
[2-3 sentences]

🐋 SMART MONEY:
[2-3 sentences]

💬 SENTIMENT:
[2-3 sentences]

🎯 RECOMMENDATION:
[3-4 sentences with specific advice]

⚠️ RISKS:
[1-2 sentences]

NO EMOJIS IN TEXT! Only in headings."""

            user_message = f"""Asset: {symbol}
Price: ${price_data.get('price', 0):.2f}
Change 24h: {price_data.get('change_24h', 0):+.2f}%

AGENT SIGNALS:
"""

        # Добавляем данные агентов
        for result in agent_results:
            agent = result.get("agent", "unknown")
            direction = result.get("direction", "HOLD")
            confidence = result.get("confidence", 0.5)
            user_message += f"- {agent.upper()}: {direction} ({confidence:.0%})\n"

        user_message += f"\nРЕЗОНАНС: {resonance['type']} ({resonance['strength']:.0%})"

        # Groq API запрос
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
            "temperature": 0.7,
            "max_tokens": 500,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()

        analysis = result["choices"][0]["message"]["content"]
        logger.info(f"✅ AI анализ получен ({len(analysis)} символов)")

        return analysis

    except Exception as e:
        logger.error(f"❌ Ошибка AI запроса: {e}")
        return "Ошибка получения AI анализа" if language == 'ru' else "Error getting AI analysis"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ГЛАВНАЯ ФУНКЦИЯ META АГЕНТА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def synthesize_decision(
    symbol: str,
    agent_results: List[Dict],
    price_data: Dict,
    language: str = 'ru'
) -> Dict:
    """Синтез финального решения"""
    logger.info(f"🧠 Meta Agent синтезирует решение для {symbol}...")

    # 1. Взвешенный score
    weighted_score = calculate_weighted_score(agent_results)

    # 2. Резонанс методов
    resonance = detect_resonance(agent_results)

    # 3. AI финальный анализ
    ai_analysis = await get_ai_final_decision(
        symbol, agent_results, resonance, price_data, language
    )

    # 4. Определяем финальное направление
    if weighted_score >= 0.65 and resonance['strength'] >= 0.6:
        final_direction = "BUY"
        final_confidence = (weighted_score + resonance['strength']) / 2
    elif weighted_score <= 0.35 and resonance['strength'] >= 0.6:
        final_direction = "SELL"
        final_confidence = (1 - weighted_score + resonance['strength']) / 2
    else:
        final_direction = "HOLD"
        final_confidence = 0.5

    result = {
        "symbol": symbol,
        "direction": final_direction,
        "confidence": final_confidence,
        "weighted_score": weighted_score,
        "resonance": resonance,
        "ai_analysis": ai_analysis,
        "agent_results": agent_results
    }

    logger.info(f"✅ ФИНАЛ: {final_direction} (confidence: {final_confidence:.2%})")

    return result
