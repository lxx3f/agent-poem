from typing import List

from app.llm.base import LLMServiceBase
from app.llm.types import LLMMessage
from app.services.message_service import MessageService


class MockLLMService(LLMServiceBase):

    def chat(self, messages: List[LLMMessage]) -> str:
        last_user_message = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        return f"[mock reply] 你刚才说的是：{last_user_message}"

    def process_message(
        self,
        message_id: int,
        response_message_id: int,
        conversation_id: int,
        user_id: int,
    ) -> None:
        """
        处理消息的示例方法
        """
        service = MessageService()
        content = f"[mock reply] 这是对消息 ID {message_id} 的回复。"
        service.update_message_content(
            message_id=response_message_id,
            content=content,
        )
        service.update_message_status(
            message_id=response_message_id,
            status="done",
        )
