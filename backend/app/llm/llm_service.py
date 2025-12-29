from typing import List, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from backend.app.core.config import settings
from backend.app.llm.base import LLMService
from backend.app.llm.types import LLMMessage
from backend.app.llm.mock import MockLLMService


class OpenAILLMService(LLMService):

    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def chat(self, messages: List[LLMMessage]) -> str:
        """
        调用 OpenAI Chat Completion
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=cast(list[ChatCompletionMessageParam], messages),
            temperature=0.7,
        )
        return response.choices[0].message.content if response.choices[
            0].message.content else ""

    def process_message(
        self,
        message_id: int,
        conversation_id: int,
        user_id: int,
    ) -> None:
        """
        处理消息的示例方法
        """
        # 这里可以添加调用 chat 方法并处理结果的逻辑
        pass


class QwenLLMService(LLMService):

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
        )
        self.model = settings.qwen_model

    def chat(self, messages: List[LLMMessage]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=cast(list[ChatCompletionMessageParam], messages),
            temperature=0.7,
        )
        return response.choices[0].message.content if response.choices[
            0].message.content else ""

    def process_message(
        self,
        message_id: int,
        conversation_id: int,
        user_id: int,
    ) -> None:
        """
        处理消息的示例方法
        """
        # 这里可以添加调用 chat 方法并处理结果的逻辑
        pass


class DeepSeekLLMService(LLMService):

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self.model = settings.deepseek_model

    def chat(self, messages: List[LLMMessage]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=cast(list[ChatCompletionMessageParam], messages),
            temperature=0.7,
        )
        return response.choices[0].message.content if response.choices[
            0].message.content else ""

    def process_message(
        self,
        message_id: int,
        conversation_id: int,
        user_id: int,
    ) -> None:
        """
        处理消息的示例方法
        """
        # 这里可以添加调用 chat 方法并处理结果的逻辑
        pass


def get_llm_service() -> LLMService:
    return MockLLMService()
    provider = settings.llm_provider

    if provider == "openai":
        return OpenAILLMService()
    if provider == "qwen":
        return QwenLLMService()
    if provider == "deepseek":
        return DeepSeekLLMService()

    raise ValueError(f"Unsupported LLM provider: {provider}")
