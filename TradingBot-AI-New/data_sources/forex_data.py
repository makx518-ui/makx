#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💱 FOREX & COMMODITIES DATA
Форекс пары + Золото, Нефть, Газ
"""

import logging
import httpx
from typing import Dict, Optional
from config import FOREX_PAIRS, COMMODITIES

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FOREX - ВАЛЮТНЫЕ ПАРЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_forex_rate(pair: str) -> Optional[Dict]:
    """Получить курс форекс пары (бесплатный API)"""
    try:
        # Используем fxratesapi.com (бесплатно)
        base, quote = pair.split("/")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.fxratesapi.com/latest",
                params={
                    "base": base,
                    "currencies": quote,
                    "resolution": "1m",
                    "amount": 1,
                    "places": 5,
                    "format": "json"
                }
            )
            response.raise_for_status()
            data = response.json()

        rate = data["rates"].get(quote)

        if rate:
            logger.info(f"✅ {pair}: {rate:.5f}")
            return {
                "pair": pair,
                "rate": float(rate),
                "timestamp": data.get("date")
            }

        return None

    except Exception as e:
        logger.error(f"❌ Ошибка форекс {pair}: {e}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMMODITIES - СЫРЬЕВЫЕ ТОВАРЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_commodity_price(symbol: str) -> Optional[Dict]:
    """Цена сырья (золото, нефть, газ)"""
    try:
        # Для commodities используем metal-api.com или альтернативы

        if symbol == "XAU/USD":  # Золото
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://data-asg.goldprice.org/dbXRates/USD"
                )
                response.raise_for_status()
                data = response.json()

            gold_price = data["items"][0]["xauPrice"]
            logger.info(f"✅ Золото: ${gold_price:.2f}/oz")

            return {
                "symbol": "XAU/USD",
                "price": float(gold_price),
                "unit": "troy ounce"
            }

        elif symbol == "XAG/USD":  # Серебро
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://data-asg.goldprice.org/dbXRates/USD"
                )
                response.raise_for_status()
                data = response.json()

            silver_price = data["items"][0]["xagPrice"]
            logger.info(f"✅ Серебро: ${silver_price:.2f}/oz")

            return {
                "symbol": "XAG/USD",
                "price": float(silver_price),
                "unit": "troy ounce"
            }

        else:
            # Для нефти и газа нужен специальный API
            logger.warning(f"⚠️ {symbol} требует платный API")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка получения {symbol}: {e}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DXY - ИНДЕКС ДОЛЛАРА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_dxy_index() -> Optional[float]:
    """Индекс доллара США (DXY) - важен для всех рынков"""
    try:
        # Используем TradingView или Yahoo Finance
        logger.info("📊 Получаю DXY...")
        # TODO: Реализовать через Yahoo Finance API
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка DXY: {e}")
        return None
