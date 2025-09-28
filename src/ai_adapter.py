"""
Optional OpenAI adapter. If OPENAI_API_KEY is set and openai is installed, uses the API.
If not available, raises RuntimeError so caller can fallback to local summarizer.

Function:
- ai_generate_summary(prompt: str, context: dict) -> str
"""
import os
from typing import Optional, Dict, Any

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

def ai_generate_summary(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    try:
        import openai
    except Exception as e:
        raise RuntimeError("openai package not installed") from e
    openai.api_key = OPENAI_KEY
    system = "You are a concise assistant. Summarize the prompt and produce clear bullets or 2-3 sentence summary."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Context:\n{context}\n\nPlease summarize:\n{prompt}"}
    ]
    resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=300, temperature=0.3)
    text = resp["choices"][0]["message"]["content"].strip()
    return text
