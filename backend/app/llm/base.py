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
