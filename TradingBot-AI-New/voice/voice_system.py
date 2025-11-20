#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎙️ VOICE SYSTEM - Голосовая система из Оракула
Распознавание и синтез речи (RU/EN)
"""

import logging
import httpx
import edge_tts
import os
import io
from config import GROQ_API_KEY, WHISPER_MODEL, VOICE

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ОПРЕДЕЛЕНИЕ ЯЗЫКА
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_language(text: str) -> str:
    """Определяет язык текста (ru или en)"""
    try:
        russian_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        total_chars = len([c for c in text if c.isalpha()])

        if total_chars == 0:
            return 'ru'

        russian_ratio = russian_chars / total_chars

        if russian_ratio > 0.3:
            return 'ru'
        else:
            return 'en'
    except:
        return 'ru'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# РАСПОЗНАВАНИЕ ГОЛОСА (Groq Whisper)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def transcribe_voice(file_path: str) -> str:
    """Распознавание голоса через Groq Whisper"""
    try:
        logger.info(f"🎤 Распознаю голос: {file_path}")

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

        # Читаем файл в память
        with open(file_path, "rb") as f:
            audio_data = f.read()

        # Используем BytesIO
        audio_file = io.BytesIO(audio_data)
        audio_file.name = os.path.basename(file_path)

        files = {"file": (audio_file.name, audio_file, "audio/ogg")}
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# СИНТЕЗ РЕЧИ (Edge TTS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def text_to_speech(text: str, output_file: str) -> bool:
    """Озвучивание текста через Edge TTS"""
    try:
        logger.info(f"🗣️ Создаю голосовое сообщение...")

        # Убираем эмодзи и спецсимволы для чистого озвучивания
        clean_text = text
        for emoji in ["📊", "🔮", "✨", "🌟", "🎯", "**", "*", "_", "📈", "📉", "🟢", "🔴", "⚠️", "💰", "🐋", "📰"]:
            clean_text = clean_text.replace(emoji, "")

        communicate = edge_tts.Communicate(clean_text, VOICE)
        await communicate.save(output_file)

        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            logger.info(f"✅ Аудио создано: {output_file}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"❌ Ошибка TTS: {e}")
        return False
