from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):

    @abstractmethod
    def run(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        输入：用户一句话 + 会话上下文
        输出：最终回复文本
        """
