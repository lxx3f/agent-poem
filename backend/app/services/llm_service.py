from typing import List, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import settings
from app.llm.base import LLMServiceBase
from app.llm.types import LLMMessage
from app.llm.mock import MockLLMService
from app.llm.OpenAI import OpenAILLMService
from app.llm.DeepSeek import DeepSeekLLMService
from app.llm.Qwen import QwenLLMService


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
