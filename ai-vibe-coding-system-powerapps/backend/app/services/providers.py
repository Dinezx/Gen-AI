from __future__ import annotations

from abc import ABC, abstractmethod
from typing import cast

import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import Settings


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout = settings.request_timeout_seconds

    async def generate(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

        return (data.get("message") or {}).get("content", "")


class OpenAIProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate(self, messages: list[dict[str, str]]) -> str:
        typed_messages = cast(list[ChatCompletionMessageParam], messages)
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=typed_messages,
            temperature=0.1,
        )
        return completion.choices[0].message.content or ""


def build_provider(provider_name: str, settings: Settings) -> LLMProvider:
    if provider_name.lower() == "openai":
        return OpenAIProvider(settings)
    return OllamaProvider(settings)
