from abc import ABC, abstractmethod
from typing import List


class RAGContext(ABC):

    @abstractmethod
    def retrieve(self, query: str) -> List[str]:
        """
        返回可直接拼入 prompt 的文本块
        """
