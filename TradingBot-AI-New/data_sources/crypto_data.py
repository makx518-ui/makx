#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪙 CRYPTO DATA - Данные по криптовалютам
Binance + CoinGecko + Whale Alert
"""

import logging
import httpx
from typing import Dict, List, Optional
from config import BINANCE_API, COINGECKO_API, CRYPTO_SYMBOLS

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BINANCE - ЦЕНЫ И ОБЪЁМЫ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_crypto_price(symbol: str) -> Optional[Dict]:
    """Получить цену крипты с Binance"""
    try:
        pair = f"{symbol}USDT"

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Ticker 24h
            response = await client.get(
                f"{BINANCE_API}/ticker/24hr",
                params={"symbol": pair}
            )
            response.raise_for_status()
            data = response.json()

        result = {
            "symbol": symbol,
            "price": float(data["lastPrice"]),
            "change_24h": float(data["priceChangePercent"]),
            "volume_24h": float(data["volume"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
        }

        logger.info(f"✅ {symbol}: ${result['price']:.2f} ({result['change_24h']:+.2f}%)")
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка получения цены {symbol}: {e}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COINGECKO - РЫНОЧНЫЕ ДАННЫЕ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_market_data(symbol: str) -> Optional[Dict]:
    """Рыночные данные с CoinGecko"""
    try:
        # Маппинг символов на CoinGecko IDs
        coin_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "MATIC": "matic-network",
            "AVAX": "avalanche-2",
            "DOT": "polkadot"
        }

        coin_id = coin_map.get(symbol)
        if not coin_id:
            return None

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{COINGECKO_API}/coins/{coin_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false"
                }
            )
            response.raise_for_status()
            data = response.json()

        market = data.get("market_data", {})

        result = {
            "market_cap": market.get("market_cap", {}).get("usd", 0),
            "total_volume": market.get("total_volume", {}).get("usd", 0),
            "circulating_supply": market.get("circulating_supply", 0),
            "ath": market.get("ath", {}).get("usd", 0),
            "atl": market.get("atl", {}).get("usd", 0),
        }

        return result

    except Exception as e:
        logger.error(f"❌ Ошибка CoinGecko для {symbol}: {e}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WHALE ALERT - КРУПНЫЕ ТРАНЗАКЦИИ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_whale_transactions(symbol: str, min_value: int = 1000000) -> List[Dict]:
    """Получить крупные транзакции китов (бесплатный API ограничен)"""
    try:
        # Whale Alert требует API ключ для production
        # Для MVP используем альтернативу или пропускаем
        logger.info(f"🐋 Whale tracking для {symbol} (требует premium API)")
        return []

    except Exception as e:
        logger.error(f"❌ Ошибка Whale Alert: {e}")
        return []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEAR & GREED INDEX
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_fear_greed_index() -> Optional[Dict]:
    """Индекс страха и жадности (0-100)"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.alternative.me/fng/")
            response.raise_for_status()
            data = response.json()

        fng = data["data"][0]
        value = int(fng["value"])
        classification = fng["value_classification"]

        logger.info(f"😱 Fear & Greed: {value}/100 ({classification})")

        return {
            "value": value,
            "classification": classification,
            "timestamp": fng["timestamp"]
        }

    except Exception as e:
        logger.error(f"❌ Ошибка Fear & Greed: {e}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ОБЩАЯ ФУНКЦИЯ - ВСЕ ДАННЫЕ ПО КРИПТОВАЛЮТЕ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_full_crypto_data(symbol: str) -> Dict:
    """Получить все данные по крипте"""
    logger.info(f"📊 Собираю данные для {symbol}...")

    price_data = await get_crypto_price(symbol)
    market_data = await get_market_data(symbol)

    result = {
        "symbol": symbol,
        "price": price_data or {},
        "market": market_data or {},
        "timestamp": None
    }

    return result
