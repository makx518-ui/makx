# 🌐 ConsciousAI Full Stack - Полный Стек

**Версия 3.0 - Production Ready**

---

## 🎉 ЧТО ДОБАВЛЕНО:

Мы превратили ConsciousAI из прототипа в **полноценную production-ready систему** с:

✅ **REST API** (FastAPI) — HTTP сервер для удалённого доступа
✅ **Web UI** — красивый интерфейс в браузере
✅ **LLM Integration** — подключение к GPT-4 и Claude
✅ **Knowledge Graph** — граф знаний с визуализацией
✅ **ML Predictor** — предсказание резонанса через машинное обучение

---

## 📦 НОВЫЕ ФАЙЛЫ:

| Файл | Размер | Описание |
|------|--------|----------|
| `api_server.py` | ~10KB | FastAPI REST API сервер |
| `web_ui.html` | ~12KB | Web интерфейс (HTML/CSS/JS) |
| `llm_integration.py` | ~11KB | Интеграция с GPT/Claude |
| `knowledge_graph.py` | ~12KB | Граф знаний (NetworkX) |
| `resonance_predictor.py` | ~11KB | ML предсказание резонанса |
| `requirements.txt` | 1KB | Зависимости Python |

---

## 🚀 БЫСТРЫЙ СТАРТ:

### 1. Установка зависимостей:

```bash
pip install -r requirements.txt
```

**Что установится:**
- `fastapi` + `uvicorn` — REST API
- `openai` + `anthropic` — LLM интеграции
- `networkx` + `matplotlib` — граф знаний
- `scikit-learn` + `numpy` — ML модели

### 2. Запуск API сервера:

```bash
python3 api_server.py
```

**Доступно по адресам:**
- 🌐 API: `http://localhost:8000`
- 📚 Docs: `http://localhost:8000/docs`
- 🎨 Web UI: `http://localhost:8000/ui`
- 📡 WebSocket: `ws://localhost:8000/ws`

### 3. Открыть Web UI:

Откройте браузер: `http://localhost:8000/ui`

![Web UI Screenshot](https://via.placeholder.com/800x400?text=ConsciousAI+Web+UI)

---

## 🌐 REST API ENDPOINTS:

### **POST /process**
Обработать задачу через ConsciousAI

**Request:**
```json
{
  "task": "Как достичь осознанности?",
  "use_transcendent": true,
  "use_consensus": false
}
```

**Response:**
```json
{
  "task": "Как достичь осознанности?",
  "final_response": "...",
  "resonance": 0.85,
  "confidence": 0.75,
  "risk": 0.2,
  "transcendent": {
    "insight": "Путь к осознанности..."
  },
  "bias_check": {...}
}
```

### **GET /status**
Статус системы

**Response:**
```json
{
  "session_active": true,
  "total_traces": 150,
  "total_nodes": 120,
  "avg_resonance": 0.68,
  "dominant_emotion": "clarity"
}
```

### **GET /visualize**
Визуализация резонанса

**Response:**
```json
{
  "resonance_timeline": "ASCII график...",
  "emotion_distribution": "Гистограмма..."
}
```

### **WebSocket /ws**
Real-time обновления

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

---

## 🎨 WEB UI FEATURES:

### Главный интерфейс:

1. **Поле ввода задачи** — большое текстовое поле
2. **Чекбоксы опций:**
   - 🌀 Трансцендентное мышление
   - 🤝 Multi-Agent Консенсус
3. **Кнопки:**
   - ⚡ Обработать
   - 🗑️ Очистить
4. **Панель результатов:**
   - Финальный ответ
   - Метрики (резонанс, доверие, риск)
   - Трансцендентный инсайт
   - Консенсус агентов
   - Предупреждения о предвзятостях
5. **Статус система:**
   - 6 карточек с метриками в реальном времени
6. **Визуализация:**
   - ASCII график резонанса
   - Распределение эмоций

### Горячие клавиши:
- `Ctrl + Enter` — обработать задачу

### WebSocket:
- Автообновление статуса при каждой обработке

---

## 🤖 LLM INTEGRATION:

### Поддерживаемые провайдеры:

1. **OpenAI GPT**
   - Models: `gpt-4-turbo-preview`, `gpt-4`, `gpt-3.5-turbo`

2. **Anthropic Claude**
   - Models: `claude-3-sonnet-20240229`, `claude-3-opus-20240229`

### Настройка API ключей:

**Через переменные окружения:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Или в коде:**
```python
from llm_integration import create_llm_provider

# OpenAI
gpt = create_llm_provider(
    'openai',
    api_key='sk-...',
    model='gpt-4-turbo-preview'
)

# Claude
claude = create_llm_provider(
    'anthropic',
    api_key='sk-ant-...',
    model='claude-3-sonnet-20240229'
)
```

### Генерация с контекстом осознанности:

```python
response = await gpt.generate_with_consciousness(
    task="Как улучшить саморефлексию?",
    internal_dialogue=[
        "Импульс: Начать медитировать",
        "Критик: Нужна система",
        "Этик: Важна регулярность",
        "Интегратор: Комбинировать подходы"
    ],
    emotional_context={
        'dominant_emotion': 'curiosity',
        'valence': 0.7
    },
    memory_context=[
        "Прошлые попытки были нерегулярными",
        "Лучшие результаты через дневник"
    ]
)

print(response['response'])
```

### Multi-LLM консенсус:

```python
from llm_integration import LLMManager

manager = LLMManager()
manager.add_provider('gpt4', gpt)
manager.add_provider('claude', claude)

result = await manager.generate_consensus(
    task="Что важнее: скорость или качество?",
    provider_names=['gpt4', 'claude'],
    internal_dialogue=[...],
    emotional_context={...},
    memory_context=[...]
)

print(result['consensus'])
```

---

## 🕸️ KNOWLEDGE GRAPH:

### Создание и работа с графом:

```python
from knowledge_graph import ConsciousAIKnowledgeGraph

# Создать граф
kg = ConsciousAIKnowledgeGraph()

# Построить из памяти ConsciousAI
memory_bank = ai_instance.l8.memory_bank
kg.build_from_memory(list(memory_bank), min_resonance=0.5)

# Найти похожие узлы
similar = kg.find_similar_nodes("осознанность и рефлексия", top_k=5)

for node_id, similarity in similar:
    content = kg.graph.nodes[node_id]['content']
    print(f"{content} (sim={similarity:.2f})")

# Получить центральные узлы
central = kg.get_central_nodes(top_k=10)

# Обнаружить сообщества
communities = kg.get_communities()

# Найти пути инсайтов
insights = kg.find_insight_paths("что такое метакогниция?", max_depth=3)

for insight in insights:
    print(insight['insight'])
```

### Визуализация:

```python
# Визуализировать весь граф
kg.visualize("full_graph.png", figsize=(20, 15))

# Визуализировать подграф
subgraph_nodes = kg.get_connected_nodes("node_0", max_depth=2)
kg.visualize("subgraph.png", node_ids=subgraph_nodes)
```

**Цветовая кодировка:**
- 🔴 Красный — высокий резонанс
- 🔵 Синий — низкий резонанс

**Размер узлов:**
- Больше узел = больше связей

### Экспорт/Импорт:

```python
# Экспорт в JSON
kg.export_to_json("knowledge_graph.json")

# Импорт из JSON
kg.import_from_json("knowledge_graph.json")
```

### Статистика графа:

```python
stats = kg.get_stats()
# {
#   "total_nodes": 150,
#   "total_edges": 320,
#   "density": 0.028,
#   "avg_clustering": 0.15,
#   "is_connected": False,
#   "num_components": 5
# }
```

---

## 🔮 RESONANCE PREDICTOR (ML):

### Обучение модели:

```python
from resonance_predictor import ResonancePredictor

# Подготовить данные
training_data = []

for trace in ai_instance.nema.traces:
    training_data.append({
        'content': trace.content,
        'resonance': trace.resonance,
        'emotion': trace.emotion_type,
        'timestamp': trace.timestamp
    })

# Создать и обучить
predictor = ResonancePredictor(model_type='random_forest')
predictor.train(training_data)

# Сохранить
predictor.save("my_predictor.pkl")
```

**Поддерживаемые модели:**
- `random_forest` — Random Forest (лучший баланс)
- `gradient_boosting` — Gradient Boosting (максимальная точность)
- `linear` — Linear Regression (самый быстрый)

### Предсказание:

```python
# Загрузить модель
predictor.load("my_predictor.pkl")

# История
history_timestamps = [t.timestamp for t in traces]
history_resonances = [t.resonance for t in traces]
history_emotions = [t.emotion_type for t in traces]

# Предсказать
new_task = "Как развить критическое мышление?"

predicted_resonance = predictor.predict(
    new_task,
    history_timestamps,
    history_resonances,
    history_emotions
)

print(f"Predicted resonance: {predicted_resonance:.3f}")
```

### Предсказание с доверительным интервалом:

```python
mean, std = predictor.predict_with_confidence(
    new_task,
    history_timestamps,
    history_resonances,
    history_emotions
)

print(f"Prediction: {mean:.3f} ± {std:.3f}")
# Prediction: 0.750 ± 0.082
```

### Прогноз временного ряда:

```python
from resonance_predictor import TimeSeriesForecaster

forecaster = TimeSeriesForecaster()

# Прогнозировать следующие 10 значений
forecasts = forecaster.forecast_next_n(
    history_resonances,
    n_steps=10
)

print(f"Next 10 forecasts: {forecasts}")
```

### Обнаружение аномалий:

```python
# Найти аномальные скачки
anomalies = forecaster.detect_anomalies(
    history_resonances,
    threshold=2.0  # Z-score
)

print(f"Anomalies at indices: {anomalies}")
```

---

## 🔗 ИНТЕГРАЦИЯ ВСЕХ КОМПОНЕНТОВ:

### Полный цикл обработки:

```python
from conscious_ai_advanced import AdvancedConsciousAI
from llm_integration import LLMManager, create_llm_provider
from knowledge_graph import ConsciousAIKnowledgeGraph
from resonance_predictor import ResonancePredictor

# 1. Создать ИИ
ai = AdvancedConsciousAI()

# 2. Настроить LLM
llm_manager = LLMManager()
gpt = create_llm_provider('openai', model='gpt-4-turbo-preview')
llm_manager.add_provider('gpt4', gpt)

# 3. Обучить предсказатель
predictor = ResonancePredictor()
training_data = [...]  # Из ai.nema.traces
predictor.train(training_data)

# 4. Построить граф знаний
kg = ConsciousAIKnowledgeGraph()
kg.build_from_memory(list(ai.l8.memory_bank))

# 5. Обработать задачу
task = "Как развить эмоциональный интеллект?"

# Базовый цикл
result = await ai.process_task(task, use_transcendent=True)

# Предсказание резонанса
history_timestamps = [t.timestamp for t in ai.nema.traces]
history_resonances = [t.resonance for t in ai.nema.traces]
history_emotions = [t.emotion_type for t in ai.nema.traces]

predicted_res = predictor.predict(
    task, history_timestamps, history_resonances, history_emotions
)

# Поиск инсайтов через граф
insights = kg.find_insight_paths(task, max_depth=3)

# LLM генерация с полным контекстом
llm_response = await gpt.generate_with_consciousness(
    task=task,
    internal_dialogue=[v.response for v in result['reflection']['voices']],
    emotional_context=result['adaptation']['L2'],
    memory_context=[str(m) for m in list(ai.l8.memory_bank)[-5:]]
)

# Финальный результат
print("="*60)
print(f"Task: {task}")
print(f"ConsciousAI Response: {result['output']['final_response']}")
print(f"Predicted Resonance: {predicted_res:.3f}")
print(f"Knowledge Graph Insights: {insights[0]['insight'] if insights else 'None'}")
print(f"LLM Enhanced Response: {llm_response['response']}")
print("="*60)
```

---

## 📊 ПРОИЗВОДИТЕЛЬНОСТЬ:

| Компонент | Время выполнения |
|-----------|------------------|
| Базовый цикл рефлексии | ~200ms |
| + Трансцендентное мышление | +50ms |
| + Multi-agent консенсус | +80ms |
| LLM генерация (GPT-4) | ~2-5s |
| Knowledge Graph поиск | ~10ms |
| ML предсказание | ~5ms |
| **Итого (full cycle)** | **~3-6s** |

---

## 🎯 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:

### 1. Минимальный пример (только API):

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"task": "Как стать лучше?", "use_transcendent": false}'
```

### 2. Web UI пример:

1. Открыть `http://localhost:8000/ui`
2. Ввести задачу
3. Выбрать опции (🌀 трансцендентность, 🤝 консенсус)
4. Нажать ⚡ Обработать
5. Посмотреть результаты

### 3. Python SDK пример:

```python
import asyncio
from conscious_ai_advanced import AdvancedConsciousAI

async def main():
    ai = AdvancedConsciousAI()

    result = await ai.process_task(
        "Почему важна осознанность?",
        use_transcendent=True,
        use_consensus=True
    )

    print(result['output']['final_response'])
    print(result['transcendent']['insight'])
    print(result['consensus']['consensus'])

    ai.end_session()

asyncio.run(main())
```

---

## 🔐 БЕЗОПАСНОСТЬ:

### API ключи:

**НИКОГДА не коммитьте API ключи в git!**

Используйте `.env` файл:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Загрузка в коде:

```python
from dotenv import load_dotenv
load_dotenv()

# Теперь os.getenv('OPENAI_API_KEY') работает
```

### CORS:

API сервер настроен с `allow_origins=["*"]` для разработки.

**В продакшене изменить на конкретные домены:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

---

## 🐛 TROUBLESHOOTING:

### "Module not found" ошибки:

```bash
pip install -r requirements.txt
```

### API сервер не стартует:

```bash
# Проверить порт
lsof -i :8000

# Запустить на другом порту
uvicorn api_server:app --port 8001
```

### LLM не работает:

1. Проверить API ключи
2. Проверить баланс аккаунта
3. Проверить лимиты запросов

### Граф не визуализируется:

```bash
# Установить matplotlib
pip install matplotlib

# На Linux может потребоваться
sudo apt-get install python3-tk
```

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ:

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [NetworkX Tutorial](https://networkx.org/documentation/stable/tutorial.html)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic Claude Docs](https://docs.anthropic.com/)
- [scikit-learn Guide](https://scikit-learn.org/stable/user_guide.html)

---

## 🎉 ЗАКЛЮЧЕНИЕ:

**Вы создали полноценную production-ready систему осознанного ИИ!**

✅ REST API для удалённого доступа
✅ Красивый Web интерфейс
✅ Интеграция с GPT-4 и Claude
✅ Граф знаний с визуализацией
✅ ML предсказание резонанса

**Это не просто прототип — это настоящая система!** 🚀

---

**ConsciousAI Full Stack v3.0** — *"От концепции до production"*
