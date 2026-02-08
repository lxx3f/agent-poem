from typing import List, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import settings
from app.llm.base import LLMServiceBase
from app.llm.types import LLMMessage
from app.llm.mock import MockLLMService
from app.llm.OpenAI import OpenAILLMService
from app.llm.DeepSeek import DeepSeekLLMService
from app.llm.Qwen import QwenLLMService


def get_llm_service() -> LLMServiceBase:
    """
    返回 LLM 服务类
    根据配置选择对应的 LLM 服务类
    
    :return: LLM 服务
    :rtype: LLMServiceBase
    """
    provider = settings.llm_provider

    if provider == "openai":
        return OpenAILLMService()
    if provider == "qwen":
        return QwenLLMService()
    if provider == "deepseek":
        return DeepSeekLLMService()

    raise ValueError(f"Unsupported LLM provider: {provider}")


class LLMService:
    """
    LLM 服务类
    """

    def __init__(self) -> None:
        self.service = get_llm_service()

    def chat(self, messages: List[LLMMessage]):
        """
        调用 LLM 服务进行对话
        
        :param messages: 对话消息
        :type messages: List[LLMMessage]
        :return: LLM 服务返回的响应
        :rtype: str
        """
        res = self.service.chat(messages)
        print("LLM Service Request:")
        print(messages)
        print("LLM Service Response:")
        print(res)
        return res
