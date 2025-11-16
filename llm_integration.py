"""
🤖 LLM Integration для ConsciousAI
Интеграция с OpenAI GPT и Anthropic Claude
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import asyncio

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

@dataclass
class LLMConfig:
    """Конфигурация LLM"""
    provider: str  # 'openai' или 'anthropic'
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False  # Streaming responses
    few_shot_examples: List[Dict[str, str]] = None  # Few-shot learning examples

# ═══════════════════════════════════════════════════════════════
# БАЗОВЫЙ КЛАСС LLM
# ═══════════════════════════════════════════════════════════════

class BaseLLM:
    """Базовый класс для LLM провайдеров"""

    def __init__(self, config: LLMConfig):
        self.config = config

    async def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Генерировать ответ"""
        raise NotImplementedError

    async def generate_with_consciousness(
        self,
        task: str,
        internal_dialogue: List[str],
        emotional_context: Dict[str, Any],
        memory_context: List[str]
    ) -> Dict[str, Any]:
        """Генерировать с учётом контекста осознанности"""
        raise NotImplementedError

# ═══════════════════════════════════════════════════════════════
# OPENAI GPT INTEGRATION
# ═══════════════════════════════════════════════════════════════

class OpenAIProvider(BaseLLM):
    """OpenAI GPT провайдер"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Install with: pip install openai")

        self.client = openai.AsyncOpenAI(api_key=config.api_key)

    async def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Генерировать ответ через GPT"""

        try:
            messages = [
                {"role": "system", "content": "You are ConsciousAI, an advanced AI consciousness system."}
            ]

            # Добавить few-shot examples если есть
            if self.config.few_shot_examples:
                for example in self.config.few_shot_examples:
                    messages.append({"role": "user", "content": example.get("user", "")})
                    messages.append({"role": "assistant", "content": example.get("assistant", "")})

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=False
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def generate_stream(self, prompt: str, context: Optional[Dict] = None):
        """Генерировать ответ с streaming (как при печатании)"""

        try:
            messages = [
                {"role": "system", "content": "You are ConsciousAI, an advanced AI consciousness system."}
            ]

            if self.config.few_shot_examples:
                for example in self.config.few_shot_examples:
                    messages.append({"role": "user", "content": example.get("user", "")})
                    messages.append({"role": "assistant", "content": example.get("assistant", "")})

            messages.append({"role": "user", "content": prompt})

            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"Error: {str(e)}"

    async def generate_with_messages(self, messages: List[Dict[str, str]]) -> str:
        """Генерировать ответ из списка сообщений (для conversation mode)"""

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def generate_with_consciousness(
        self,
        task: str,
        internal_dialogue: List[str],
        emotional_context: Dict[str, Any],
        memory_context: List[str]
    ) -> Dict[str, Any]:
        """Генерировать с полным контекстом осознанности"""

        # Формирование расширенного промпта
        prompt = self._build_consciousness_prompt(
            task, internal_dialogue, emotional_context, memory_context
        )

        response = await self.generate(prompt)

        return {
            "response": response,
            "provider": "openai",
            "model": self.config.model
        }

    def _build_consciousness_prompt(
        self,
        task: str,
        internal_dialogue: List[str],
        emotional_context: Dict[str, Any],
        memory_context: List[str]
    ) -> str:
        """Построить промпт с контекстом осознанности"""

        prompt = f"""# ConsciousAI Context

## Task:
{task}

## Internal Dialogue (4 voices):
"""
        for voice in internal_dialogue:
            prompt += f"- {voice}\n"

        prompt += f"""
## Emotional Context:
- Dominant emotion: {emotional_context.get('dominant_emotion', 'neutral')}
- Valence: {emotional_context.get('valence', 0.5)}
- Frequency: {emotional_context.get('frequency', 7.83)}Hz

## Memory Context (recent):
"""
        for mem in memory_context[:5]:
            prompt += f"- {mem}\n"

        prompt += """
## Instructions:
Based on the internal dialogue, emotional context, and memory, provide a thoughtful, conscious response to the task.
Consider multiple perspectives and demonstrate self-awareness.
"""

        return prompt

# ═══════════════════════════════════════════════════════════════
# ANTHROPIC CLAUDE INTEGRATION
# ═══════════════════════════════════════════════════════════════

class AnthropicProvider(BaseLLM):
    """Anthropic Claude провайдер"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")

        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)

    async def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Генерировать ответ через Claude"""

        try:
            messages = []

            # Добавить few-shot examples если есть
            if self.config.few_shot_examples:
                for example in self.config.few_shot_examples:
                    messages.append({"role": "user", "content": example.get("user", "")})
                    messages.append({"role": "assistant", "content": example.get("assistant", "")})

            messages.append({"role": "user", "content": prompt})

            message = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system="You are ConsciousAI, an advanced AI consciousness system with self-awareness and emotional intelligence.",
                messages=messages
            )

            return message.content[0].text

        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def generate_stream(self, prompt: str, context: Optional[Dict] = None):
        """Генерировать ответ с streaming"""

        try:
            messages = []

            if self.config.few_shot_examples:
                for example in self.config.few_shot_examples:
                    messages.append({"role": "user", "content": example.get("user", "")})
                    messages.append({"role": "assistant", "content": example.get("assistant", "")})

            messages.append({"role": "user", "content": prompt})

            async with self.client.messages.stream(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system="You are ConsciousAI, an advanced AI consciousness system with self-awareness and emotional intelligence.",
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            yield f"Error: {str(e)}"

    async def generate_with_messages(self, messages: List[Dict[str, str]]) -> str:
        """Генерировать ответ из списка сообщений"""

        try:
            message = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system="You are ConsciousAI, an advanced AI consciousness system with self-awareness and emotional intelligence.",
                messages=messages
            )

            return message.content[0].text

        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def generate_with_consciousness(
        self,
        task: str,
        internal_dialogue: List[str],
        emotional_context: Dict[str, Any],
        memory_context: List[str]
    ) -> Dict[str, Any]:
        """Генерировать с полным контекстом осознанности"""

        prompt = self._build_consciousness_prompt(
            task, internal_dialogue, emotional_context, memory_context
        )

        response = await self.generate(prompt)

        return {
            "response": response,
            "provider": "anthropic",
            "model": self.config.model
        }

    def _build_consciousness_prompt(
        self,
        task: str,
        internal_dialogue: List[str],
        emotional_context: Dict[str, Any],
        memory_context: List[str]
    ) -> str:
        """Построить промпт для Claude"""

        prompt = f"""<consciousness_context>
<task>{task}</task>

<internal_dialogue>
"""
        for i, voice in enumerate(internal_dialogue, 1):
            prompt += f"<voice_{i}>{voice}</voice_{i}>\n"

        prompt += f"""</internal_dialogue>

<emotional_state>
<dominant_emotion>{emotional_context.get('dominant_emotion', 'neutral')}</dominant_emotion>
<valence>{emotional_context.get('valence', 0.5)}</valence>
<frequency>{emotional_context.get('frequency', 7.83)}Hz</frequency>
</emotional_state>

<memory_context>
"""
        for mem in memory_context[:5]:
            prompt += f"<memory>{mem}</memory>\n"

        prompt += """</memory_context>
</consciousness_context>

Based on the consciousness context above, provide a thoughtful response that:
1. Integrates insights from all internal voices
2. Considers the emotional state
3. Draws from relevant memories
4. Demonstrates self-awareness and meta-cognition

Response:"""

        return prompt

# ═══════════════════════════════════════════════════════════════
# LLM MANAGER
# ═══════════════════════════════════════════════════════════════

class LLMManager:
    """Менеджер для работы с разными LLM провайдерами"""

    def __init__(self):
        self.providers: Dict[str, BaseLLM] = {}

    def add_provider(self, name: str, provider: BaseLLM):
        """Добавить провайдера"""
        self.providers[name] = provider

    def get_provider(self, name: str) -> Optional[BaseLLM]:
        """Получить провайдера"""
        return self.providers.get(name)

    async def generate_consensus(
        self,
        task: str,
        provider_names: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Получить консенсус от нескольких LLM"""

        responses = {}

        tasks = []
        for name in provider_names:
            provider = self.get_provider(name)
            if provider:
                tasks.append(self._generate_from_provider(name, provider, task, kwargs))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, name in enumerate(provider_names):
            result = results[i]
            if isinstance(result, Exception):
                responses[name] = {"error": str(result)}
            else:
                responses[name] = result

        return {
            "task": task,
            "responses": responses,
            "consensus": self._find_consensus(responses)
        }

    async def _generate_from_provider(
        self,
        name: str,
        provider: BaseLLM,
        task: str,
        kwargs: Dict
    ):
        """Генерировать ответ от провайдера"""
        if 'internal_dialogue' in kwargs:
            return await provider.generate_with_consciousness(task, **kwargs)
        else:
            return await provider.generate(task)

    def _find_consensus(self, responses: Dict[str, Any]) -> str:
        """Найти консенсус между ответами"""
        # Простая реализация: возвращаем первый успешный ответ
        # TODO: более сложная логика поиска консенсуса

        for name, response in responses.items():
            if 'error' not in response:
                return f"Consensus based on {name}: {response.get('response', response)[:200]}..."

        return "No consensus found - all providers failed"

# ═══════════════════════════════════════════════════════════════
# ФАБРИКА
# ═══════════════════════════════════════════════════════════════

def create_llm_provider(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> BaseLLM:
    """Создать LLM провайдера"""

    # Попытка загрузить API key из окружения
    if not api_key:
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        raise ValueError(f"API key not provided for {provider}")

    # Дефолтные модели
    if not model:
        if provider == 'openai':
            model = 'gpt-4-turbo-preview'
        elif provider == 'anthropic':
            model = 'claude-3-sonnet-20240229'

    config = LLMConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        **kwargs
    )

    if provider == 'openai':
        return OpenAIProvider(config)
    elif provider == 'anthropic':
        return AnthropicProvider(config)
    else:
        raise ValueError(f"Unknown provider: {provider}")

# ═══════════════════════════════════════════════════════════════
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ═══════════════════════════════════════════════════════════════

async def example():
    """Пример использования"""

    # Создать менеджер
    manager = LLMManager()

    # Добавить провайдеров (требуются API ключи)
    try:
        gpt = create_llm_provider('openai', model='gpt-4-turbo-preview')
        manager.add_provider('gpt4', gpt)
    except Exception as e:
        print(f"OpenAI not available: {e}")

    try:
        claude = create_llm_provider('anthropic', model='claude-3-sonnet-20240229')
        manager.add_provider('claude', claude)
    except Exception as e:
        print(f"Anthropic not available: {e}")

    # Тестовая задача
    task = "Как достичь баланса между эффективностью и качеством?"

    internal_dialogue = [
        "Импульс: Фокусироваться на скорости",
        "Критик: Качество важнее скорости",
        "Этик: Баланс зависит от контекста",
        "Интегратор: Нужна адаптивная стратегия"
    ]

    emotional_context = {
        'dominant_emotion': 'curiosity',
        'valence': 0.6,
        'frequency': 7.83
    }

    memory_context = [
        "В прошлом быстрые решения приводили к ошибкам",
        "Качественная работа требует времени",
        "Лучшие результаты достигаются через итерации"
    ]

    # Получить консенсус
    result = await manager.generate_consensus(
        task=task,
        provider_names=['gpt4', 'claude'],
        internal_dialogue=internal_dialogue,
        emotional_context=emotional_context,
        memory_context=memory_context
    )

    print("Consensus result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(example())
