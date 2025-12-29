from typing import List

from backend.app.llm.base import LLMService
from backend.app.llm.types import LLMMessage


class MockLLMService(LLMService):

    def chat(self, messages: List[LLMMessage]) -> str:
        last_user_message = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        return f"[mock reply] 你刚才说的是：{last_user_message}"
