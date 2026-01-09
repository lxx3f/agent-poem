from typing import List, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from backend.app.core.config import settings
from backend.app.llm.base import LLMServiceBase
from backend.app.llm.types import LLMMessage
from backend.app.llm.mock import MockLLMService
from backend.app.llm.OpenAI import OpenAILLMService
from backend.app.llm.DeepSeek import DeepSeekLLMService
from backend.app.llm.Qwen import QwenLLMService


def get_llm_service() -> LLMServiceBase:
    # return MockLLMService()
    provider = settings.llm_provider

    if provider == "openai":
        return OpenAILLMService()
    if provider == "qwen":
        return QwenLLMService()
    if provider == "deepseek":
        return DeepSeekLLMService()

    raise ValueError(f"Unsupported LLM provider: {provider}")


class LLMService:

    def __init__(self) -> None:
        self.service = get_llm_service()

    def chat(self, messages: List[LLMMessage]):
        return self.service.chat(messages)
