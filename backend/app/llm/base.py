from abc import ABC, abstractmethod
from typing import List

from backend.app.llm.types import LLMMessage


class LLMService(ABC):
    """
    LLM 服务抽象层
    """

    @abstractmethod
    def chat(self, messages: List[LLMMessage]) -> str:
        """
        同步对话接口（最小闭环）

        :param messages: 已构造好的 LLM messages
        :return: assistant 的文本回复
        """
        raise NotImplementedError

    @abstractmethod
    def process_message(
        self,
        message_id: int,
        response_message_id: int,
        conversation_id: int,
        user_id: int,
    ) -> None:
        """
        处理消息的示例方法

        :param message_id: 消息 ID
        :param response_message_id: 响应消息 ID
        :param conversation_id: 会话 ID
        :param user_id: 用户 ID
        """
        raise NotImplementedError
