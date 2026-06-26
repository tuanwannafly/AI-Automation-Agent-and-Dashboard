from abc import ABC, abstractmethod
from typing import AsyncGenerator
from ..models.schemas import Message

class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completion"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the provider is available"""
        pass

class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            from groq import AsyncGroq
            self._client = AsyncGroq(api_key=self.api_key)
        return self._client
    
    async def chat(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def test_connection(self) -> bool:
        try:
            async for _ in self.chat([{"role": "user", "content": "Hi"}]):
                pass
            return True
        except Exception:
            return False

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client
    
    async def chat(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def test_connection(self) -> bool:
        try:
            async for _ in self.chat([{"role": "user", "content": "Hi"}]):
                pass
            return True
        except Exception:
            return False

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client
    
    async def chat(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        from google.generativeai.types import GenerationConfig
        
        prompt = messages[-1]["content"] if messages else ""
        response = self.client.generate_content(
            prompt,
            stream=True,
            generation_config=GenerationConfig(**kwargs) if kwargs else None
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    async def test_connection(self) -> bool:
        try:
            async for _ in self.chat([{"role": "user", "content": "Hi"}]):
                pass
            return True
        except Exception:
            return False

def get_provider(provider: str, api_key: str) -> BaseLLMProvider:
    providers = {
        "groq": GroqProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
    }
    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}")
    return providers[provider](api_key)