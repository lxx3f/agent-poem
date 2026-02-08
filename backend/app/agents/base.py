from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.services.llm_service import LLMService


class BaseAgentLoop(ABC):
    """
    Agent Loop 基类
    """

    def __init__(self):
        pass
