from typing import List, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from backend.app.core.config import settings
from backend.app.llm.base import LLMServiceBase
from backend.app.llm.types import LLMMessage


class QwenLLMService(LLMServiceBase):

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
