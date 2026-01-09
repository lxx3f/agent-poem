from typing import List

from backend.app.llm.types import LLMMessage
from backend.app.services.llm_service import LLMService
from backend.app.services.mysql_service import MySQLService
from backend.app.services.conversation_service import ConversationService
from backend.app.services.message_service import MessageService
from backend.app.services.poetry_service import PoetryService


class PoetryGameWorkflow:
    """
    飞花令 / 诗词游戏工作流
    """

    def __init__(self):
        self.llm = LLMService()
        self.mysql_service = MySQLService()
        self.conversation_service = ConversationService()
        self.message_agent = MessageService()

    def run(
        self,
        conversation_id: int,
        user_id: int,
        user_input: str,
        history_limit: int = 200,
    ) -> str:
        '''
        运行工作流，保存消息到数据库，返回LLM回复
        
        :param conversation_id: 会话 ID
        :type conversation_id: int
        :param user_id: 用户 ID
        :type user_id: int
        :param user_input: 用户输入
        :type user_input: str
        :param history_limit: 历史消息限制
        :type history_limit: int
        :return: LLM 回复
        :rtype: str
        '''
        # 1. 获取会话 & Agent
        conversation = self.conversation_service.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )
        agent = self.mysql_service.get_agent_by_id(conversation["agent_id"])

        messages: List[LLMMessage] = []

        # 2. system message（规则prompt）
        messages.append(
            LLMMessage(
                role="system",
                content=agent["system_prompt"],
            ))

        # 3. 历史消息（用于避免重复 & 维持轮次）
        history = self.message_agent.get_messages_by_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=history_limit,
        )

        for msg in history:
            messages.append(
                LLMMessage(
                    role=msg["role"],
                    content=msg["content"],
                ))

        # 4. 当前用户输入
        messages.append(LLMMessage(
            role="user",
            content=user_input,
        ))
        user_message_id = self.message_agent.create_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            status="pending",
            content=user_input,
        )

        # 5. LLM 裁判 + 应答
        assistant_reply = self.llm.chat(messages)
        self.message_agent.create_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            status="done",
            content=assistant_reply,
        )
        self.message_agent.update_message_status(
            message_id=user_message_id,
            status="done",
        )

        return assistant_reply
