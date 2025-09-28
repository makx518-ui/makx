"""
Lightweight VLX runtime/engine.

Features:
- loads parsed VLX dict
- manages triggers and resonance memory
- can persist memory to a JSON file
- generate_summary() is pluggable: uses ai_adapter if available, otherwise a simple local summarizer
"""
import json
import os
from typing import List, Dict, Any, Optional

MEMORY_FILENAME = "vlx_memory.json"

class VlxEngine:
    def __init__(self, parsed: Dict[str, Any], memory_path: Optional[str] = None):
        self.parsed = parsed
        self.memory_path = memory_path or MEMORY_FILENAME
        self.resonance_memory: List[Any] = []
        self.pending_idea: Optional[str] = None
        # default triggers based on file
        self.trigger_active = {"⚡️∞": False, "❤️🚫": False}
        # load persisted memory if exists
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.resonance_memory = data.get("resonance_memory", [])
            except Exception:
                self.resonance_memory = []

    def _save_memory(self):
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump({"resonance_memory": self.resonance_memory}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def activate_trigger(self, name: str):
        if name in self.trigger_active:
            self.trigger_active[name] = True

    def deactivate_trigger(self, name: str):
        if name in self.trigger_active:
            self.trigger_active[name] = False

    def capture_signal(self, signal: Dict[str, Any]):
        if not self.trigger_active.get("⚡️∞", False):
            return
        # normalize: ensure intensity 0..1 if provided
        try:
            intensity = float(signal.get("intensity", 1))
            intensity = max(0.0, min(1.0, intensity))
            signal["intensity"] = intensity
        except Exception:
            signal["intensity"] = 1.0
        self.resonance_memory.append(signal)
        self._save_memory()

    def trigger_insight(self, amplitude: Any):
        if not self.trigger_active.get("⚡️∞", False):
            return
        if isinstance(amplitude, str):
            self.pending_idea = amplitude
        else:
            self.pending_idea = self._local_summarize(amplitude)

    def update_resonance(self):
        if not self.trigger_active.get("⚡️∞", False):
            return
        if self.resonance_memory:
            self.pending_idea = self._local_summarize(self.resonance_memory[-10:])

    def on_session_complete(self):
        if not self.trigger_active.get("❤️🚫", False):
            return None
        if not self.pending_idea:
            self.pending_idea = self._local_summarize(self.resonance_memory)
        summary = self.generate_summary(self.pending_idea)
        tw = self.parsed.get("task_window") or "CONTEXT:....."
        session_number = self._get_next_session_number(tw)
        tw_new = f"{tw}\n\n[Выжимка сессии {session_number}]: {summary}"
        self.parsed["task_window"] = tw_new
        self.pending_idea = None
        self.resonance_memory = []
        self._save_memory()
        for k in self.trigger_active:
            self.trigger_active[k] = False
        return summary

    def _get_next_session_number(self, task_window_text: str) -> int:
        return task_window_text.count("[Выжимка сессии") + 1

    def _local_summarize(self, data: Any) -> str:
        if isinstance(data, str):
            txt = data
            return txt.strip()
        if isinstance(data, list):
            parts = []
            for item in data:
                if isinstance(item, dict):
                    if "text" in item:
                        parts.append(str(item["text"]))
                    else:
                        parts.append(" ".join(str(v) for v in item.values()))
                else:
                    parts.append(str(item))
            joined = " | ".join(p for p in parts if p)
            return (joined[:800] + "...") if len(joined) > 800 else joined
        return str(data)

    def generate_summary(self, prompt: str) -> str:
        try:
            from src.ai_adapter import ai_generate_summary
            return ai_generate_summary(prompt, context=self.parsed)
        except Exception:
            return self._local_summarize(prompt)