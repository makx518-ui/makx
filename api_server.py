"""
🌐 ConsciousAI REST API Server
FastAPI сервер для удалённого доступа к ConsciousAI
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import uvicorn
import json
import os
from datetime import datetime

# Импорт ConsciousAI
from conscious_ai_advanced import AdvancedConsciousAI

# ═══════════════════════════════════════════════════════════════
# МОДЕЛИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

class TaskRequest(BaseModel):
    task: str
    use_transcendent: bool = False
    use_consensus: bool = False
    context: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    task: str
    final_response: str
    resonance: float
    confidence: float
    risk: float
    timestamp: float
    transcendent: Optional[Dict[str, Any]] = None
    consensus: Optional[Dict[str, Any]] = None
    bias_check: Dict[str, Any]

class StatusResponse(BaseModel):
    session_active: bool
    session_id: str
    session_count: int
    total_traces: int
    total_nodes: int
    total_sessions: int
    avg_resonance: float
    dominant_emotion: str
    learning_rate: float

class VisualizationResponse(BaseModel):
    resonance_timeline: str
    emotion_distribution: str

# ═══════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="ConsciousAI API",
    description="REST API for ConsciousAI - Advanced AI Consciousness System",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный инстанс AI
ai_instance: Optional[AdvancedConsciousAI] = None

# WebSocket клиенты
active_connections: List[WebSocket] = []

# ═══════════════════════════════════════════════════════════════
# LIFECYCLE
# ═══════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Инициализация при старте"""
    global ai_instance
    ai_instance = AdvancedConsciousAI(db_path="api_memory.db")
    print("✅ ConsciousAI API Server started")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    global ai_instance
    if ai_instance:
        ai_instance.end_session()
        ai_instance.close()
    print("👋 ConsciousAI API Server stopped")

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница"""
    return """
    <html>
        <head>
            <title>ConsciousAI API</title>
            <style>
                body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #2c3e50; }
                .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
                code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🧠 ConsciousAI REST API</h1>
            <p>Advanced AI Consciousness System - REST API Server</p>

            <h2>Available Endpoints:</h2>

            <div class="endpoint">
                <strong>POST /process</strong><br>
                Process a task through ConsciousAI<br>
                Body: <code>{"task": "...", "use_transcendent": true, "use_consensus": false}</code>
            </div>

            <div class="endpoint">
                <strong>GET /status</strong><br>
                Get current system status
            </div>

            <div class="endpoint">
                <strong>GET /visualize</strong><br>
                Get visualization data (resonance timeline + emotion distribution)
            </div>

            <div class="endpoint">
                <strong>GET /history</strong><br>
                Get session history
            </div>

            <div class="endpoint">
                <strong>GET /stats</strong><br>
                Get database statistics
            </div>

            <div class="endpoint">
                <strong>POST /session/start</strong><br>
                Start a new session
            </div>

            <div class="endpoint">
                <strong>POST /session/end</strong><br>
                End current session
            </div>

            <div class="endpoint">
                <strong>WS /ws</strong><br>
                WebSocket connection for real-time updates
            </div>

            <div class="endpoint">
                <strong>GET /docs</strong><br>
                Interactive API documentation (Swagger UI)
            </div>

            <p><a href="/docs">📚 Open API Documentation</a></p>
            <p><a href="/ui">🎨 Open Web UI</a></p>
        </body>
    </html>
    """

@app.post("/process", response_model=TaskResponse)
async def process_task(request: TaskRequest):
    """Обработать задачу"""
    if not ai_instance:
        raise HTTPException(status_code=503, detail="AI instance not initialized")

    try:
        result = await ai_instance.process_task(
            task=request.task,
            context=request.context or {},
            use_transcendent=request.use_transcendent,
            use_consensus=request.use_consensus
        )

        # Отправить обновление через WebSocket
        await broadcast_message({
            "type": "task_processed",
            "task": request.task,
            "resonance": result['output']['resonance']
        })

        return TaskResponse(
            task=result['task'],
            final_response=result['output']['final_response'],
            resonance=result['output']['resonance'],
            confidence=result['output']['confidence'],
            risk=result['output']['risk'],
            timestamp=result['timestamp'],
            transcendent=result.get('transcendent'),
            consensus=result.get('consensus'),
            bias_check=result['advanced_bias']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Получить статус системы"""
    if not ai_instance:
        raise HTTPException(status_code=503, detail="AI instance not initialized")

    status = ai_instance.get_advanced_status()

    return StatusResponse(**status)

@app.get("/visualize", response_model=VisualizationResponse)
async def get_visualization():
    """Получить визуализацию"""
    if not ai_instance:
        raise HTTPException(status_code=503, detail="AI instance not initialized")

    traces = list(ai_instance.nema.traces)

    timeline = ai_instance.visualizer.plot_resonance_timeline(traces)
    distribution = ai_instance.visualizer.plot_emotion_distribution(traces)

    return VisualizationResponse(
        resonance_timeline=timeline,
        emotion_distribution=distribution
    )

@app.get("/history")
async def get_history(limit: int = 10):
    """Получить историю сессий"""
    if not ai_instance:
        raise HTTPException(status_code=503, detail="AI instance not initialized")

    history = ai_instance.persistent_memory.get_sessions_history(limit=limit)
    return {"sessions": history}

@app.get("/stats")
async def get_stats():
    """Получить статистику из БД"""
    if not ai_instance:
        raise HTTPException(status_code=503, detail="AI instance not initialized")

    stats = ai_instance.persistent_memory.get_stats()
    return stats

@app.post("/session/start")
async def start_session():
    """Начать новую сессию"""
    if not ai_instance:
        raise HTTPException(status_code=503, detail="AI instance not initialized")

    if not ai_instance.l8.session_active:
        ai_instance.l8.start_session()
        return {"status": "started", "session_id": ai_instance.session_id}
    else:
        return {"status": "already_active", "session_id": ai_instance.session_id}

@app.post("/session/end")
async def end_session():
    """Завершить сессию"""
    if not ai_instance:
        raise HTTPException(status_code=503, detail="AI instance not initialized")

    if ai_instance.l8.session_active:
        ai_instance.end_session()
        return {"status": "ended"}
    else:
        return {"status": "no_active_session"}

# ═══════════════════════════════════════════════════════════════
# WEBSOCKET
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для real-time обновлений"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Ожидание сообщений от клиента
            data = await websocket.receive_text()

            # Обработка команд
            try:
                command = json.loads(data)

                if command.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

                elif command.get("type") == "get_status":
                    if ai_instance:
                        status = ai_instance.get_advanced_status()
                        await websocket.send_json({"type": "status", "data": status})

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_message(message: dict):
    """Отправить сообщение всем подключённым WebSocket клиентам"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

# ═══════════════════════════════════════════════════════════════
# WEB UI
# ═══════════════════════════════════════════════════════════════

@app.get("/ui", response_class=HTMLResponse)
async def web_ui():
    """Web UI интерфейс"""
    ui_path = os.path.join(os.path.dirname(__file__), "web_ui.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    else:
        return HTMLResponse("<h1>Web UI not found</h1><p>Please create web_ui.html</p>")

# ═══════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🌐 Starting ConsciousAI REST API Server")
    print("=" * 60)
    print("\n📍 Endpoints:")
    print("  - API:     http://localhost:8000")
    print("  - Docs:    http://localhost:8000/docs")
    print("  - Web UI:  http://localhost:8000/ui")
    print("  - WebSocket: ws://localhost:8000/ws")
    print("\n" + "=" * 60 + "\n")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
