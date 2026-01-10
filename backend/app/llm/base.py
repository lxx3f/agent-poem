from abc import ABC, abstractmethod
from typing import List

from app.llm.types import LLMMessage


class LLMServiceBase(ABC):
    """
    LLM 服务抽象层
    """

    @abstractmethod
    def chat(self, messages: List[LLMMessage]) -> str:
        """
        同步对话接口

        :param messages: 已构造好的 LLM messages
        :return: assistant 的文本回复
        """
        raise NotImplementedError
