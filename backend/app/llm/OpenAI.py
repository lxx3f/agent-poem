from typing import List, cast
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import settings
from app.llm.base import LLMServiceBase
from app.llm.types import LLMMessage


class OpenAILLMService(LLMServiceBase):

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
