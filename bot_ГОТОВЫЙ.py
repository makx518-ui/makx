#!/usr/bin/env python3
import asyncio
import logging
import httpx
import os
import json
import threading
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки (ВСТАВЬ СВОИ ТОКЕНЫ ПЕРЕД ЗАГРУЗКОЙ НА AMVERA!)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "ВСТАВЬ_СЮДА_СВОЙ_GROQ_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "ВСТАВЬ_СЮДА_СВОЙ_TELEGRAM_TOKEN")
DATA_DIR = "data/dreams"
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8080")

os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Веб-сервер
async def handle_static(request):
    """Раздача статических файлов"""
    path = request.match_info.get('path', 'index.html')

    # ↓↓↓ ИЗМЕНЕНИЕ 1: Добавил demo.html и видео ↓↓↓
    static_files = ['index.html', 'style.css', 'app.js', 'Оракул.html', 'demo.html', 'Космическая Одиссея.mp4']

    if path in static_files and os.path.exists(path):
        return web.FileResponse(path)
    return web.Response(text="Not Found", status=404)

async def handle_dream_api(request):
    """API для получения данных сна"""
    dream_id = request.match_info.get('id')
    file_path = os.path.join(DATA_DIR, f"{dream_id}.json")

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return web.json_response(data)
    return web.json_response({"error": "Dream not found"}, status=404)

def run_web_server():
    """Запуск веб-сервера в отдельном потоке"""
    async def start_server():
        app = web.Application()
        app.router.add_get('/api/dream/{id}', handle_dream_api)
        app.router.add_get('/{path:.*}', handle_static)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logger.info("✅ Веб-сервер запущен на порту 8080")

        # Держим сервер запущенным
        await asyncio.Event().wait()

    # Создаем новый event loop для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())

# Telegram бот
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    # ↓↓↓ ИЗМЕНЕНИЕ 2: Добавил кнопку для демо ↓↓↓
    keyboard = [
        [InlineKeyboardButton("📊 Визуализация сна", web_app=WebAppInfo(url=f"{WEBAPP_URL}/index.html"))],
        [InlineKeyboardButton("🎬 Посмотреть ДЕМО-ВИДЕО", web_app=WebAppInfo(url=f"{WEBAPP_URL}/demo.html"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌙 *Оракул Снов*\n\n"
        "Расскажи свой сон текстом!\n"
        "Я создам интерактивную визуализацию 📊\n\n"
        "🎬 Посмотри ДЕМО перед использованием!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста сна"""
    dream_text = update.message.text
    user_id = update.effective_user.id

    await update.message.reply_text("🌙 Анализирую твой сон...")

    # AI анализ
    dream_data = await analyze_dream_with_ai(dream_text, user_id)

    # Сохраняем данные
    dream_id = f"{user_id}_{int(datetime.now().timestamp())}"
    file_path = os.path.join(DATA_DIR, f"{dream_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(dream_data, f, ensure_ascii=False, indent=2)

    # Отправляем трактовку + кнопку визуализации
    keyboard = [[InlineKeyboardButton("📊 Открыть визуализацию", web_app=WebAppInfo(url=f"{WEBAPP_URL}/index.html?id={dream_id}"))]]

    await update.message.reply_text(
        f"✨ *Трактовка сна:*\n\n{dream_data['interpretation']}\n\n"
        f"🔮 Ключевые символы: {', '.join([s['name'] for s in dream_data['symbols'][:3]])}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def analyze_dream_with_ai(dream_text: str, user_id: int):
    """AI анализ сна"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "Ты эксперт по толкованию снов. Анализируй сны кратко и структурированно."},
                        {"role": "user", "content": f"Проанализируй сон: {dream_text}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                interpretation = result['choices'][0]['message']['content']

                return {
                    "id": f"{user_id}_{int(datetime.now().timestamp())}",
                    "text": dream_text,
                    "interpretation": interpretation,
                    "symbols": [
                        {"name": "Символ 1", "meaning": "Значение", "connections": []},
                        {"name": "Символ 2", "meaning": "Значение", "connections": []},
                        {"name": "Символ 3", "meaning": "Значение", "connections": []}
                    ],
                    "emotions": [
                        {"time": "Начало", "emotion": "Интерес", "intensity": 7},
                        {"time": "Развитие", "emotion": "Эмоция", "intensity": 6}
                    ],
                    "archetypes": [
                        {"name": "Искатель", "icon": "🧭", "description": "Поиск", "manifestation": "Проявление"}
                    ],
                    "insights": [
                        {"icon": "💡", "title": "Инсайт", "text": "Текст"}
                    ],
                    "metrics": {
                        "emotionalBalance": 7,
                        "intensity": 6,
                        "lucidity": 5,
                        "symbolDensity": 3
                    }
                }
    except Exception as e:
        logger.error(f"Ошибка AI: {e}")

    # Fallback
    return {
        "id": f"{user_id}_{int(datetime.now().timestamp())}",
        "text": dream_text,
        "interpretation": "Твой сон отражает внутренние переживания.",
        "symbols": [{"name": "Символ", "meaning": "Значение", "connections": []}],
        "emotions": [{"time": "Начало", "emotion": "Интерес", "intensity": 7}],
        "archetypes": [{"name": "Искатель", "icon": "🧭", "description": "Поиск", "manifestation": "Проявление"}],
        "insights": [{"icon": "💡", "title": "Инсайт", "text": "Текст"}],
        "metrics": {"emotionalBalance": 7, "intensity": 6, "lucidity": 5, "symbolDensity": 3}
    }

def main():
    """Главная функция"""
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    logger.info("🌐 Веб-сервер запускается...")

    # Запускаем бота
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dream))

    logger.info("🌙 Оракул Снов запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
