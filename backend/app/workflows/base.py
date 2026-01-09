from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseWorkflow(ABC):
    """
    所有 Agent Workflow 的抽象基类
    """

    def __init__(self, agent: Dict[str, Any]):
        self.agent = agent

    @abstractmethod
    def run(
        self,
        user_input: str,
        conversation_id: int,
        user_id: int,
    ) -> str:
        """
        执行 workflow，返回 LLM 最终输出文本
        """
        pass
