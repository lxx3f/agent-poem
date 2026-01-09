from typing import List

import logging
from backend.app.llm.types import LLMMessage
from backend.app.services.llm_service import LLMService
from backend.app.services.poetry_service import PoetryService
from backend.app.services.conversation_service import ConversationService
from backend.app.services.message_service import MessageService
from backend.app.services.mysql_service import MySQLService


class RagChatWorkflow:

    def __init__(self):
        """
        初始化服务实例
        
        创建并初始化多个服务对象，包括大语言模型服务、诗歌服务、
        对话服务、智能体服务和消息服务，为后续的功能调用提供基础服务支持。
        
        Args:
            None
            
        Returns:
            None
        """
        self.llm = LLMService()
        self.poetry_service = PoetryService()
        self.conversation_service = ConversationService()
        self.mysql_service = MySQLService()
        self.message_service = MessageService()

    def run(
        self,
        conversation_id: int,
        user_id: int,
        user_input: str,
        top_k: int = 5,
        history_limit: int = 10,
    ) -> str:
        """
        执行 RAG + Chat 工作流，将消息保存到数据库中，返回助手回复。

        Args:
            conversation_id (int): 会话ID
            user_id (int): 用户ID
            user_input (str): 用户输入内容
            top_k (int, optional): RAG检索返回的最相似结果数量，默认为5
            history_limit (int, optional): 历史消息限制数量，默认为10

        Returns:
            str: 助手回复内容
        """

        # 1. 获取会话 & Agent
        conversation = self.conversation_service.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )
        agent = self.mysql_service.get_agent_by_id(conversation["agent_id"])

        # 2. system message（Agent Prompt）
        messages: List[LLMMessage] = [
            LLMMessage(
                role="system",
                content=agent["system_prompt"],
            )
        ]
        logging.info(f"[Agent Prompt] {agent['system_prompt']}")

        # 3. 历史消息（裁剪后）
        history = self.message_service.get_messages_by_conversation(
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

        # 4. RAG 检索
        poems = self.poetry_service.search(
            query=user_input,
            search_type="vector",
            top_k=top_k,
        )

        if poems:
            rag_context = "\n\n".join(
                f"《{p['title']}》 {p['writer']}\n{p['content']}" for p in poems)

            messages.append(
                LLMMessage(
                    role="system",
                    content=("以下是与用户问题相关的诗词资料，可供参考：\n\n"
                             f"{rag_context}"),
                ))
            logging.info(f"[RAG Context] {rag_context}")

        # 5. 插入当前用户输入
        messages.append(LLMMessage(
            role="user",
            content=user_input,
        ))
        user_message_id = self.message_service.create_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            status="pending",
            content=user_input,
        )
        logging.info(f"[User Input] {user_input}")

        # 6. 调用 LLM
        assistant_reply = self.llm.chat(messages)

        # 7. 保存消息 & 更新状态
        self.message_service.create_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            status="done",
            content=assistant_reply,
        )
        self.message_service.update_message_status(
            message_id=user_message_id,
            status="done",
        )
        logging.info(f"[Assistant Reply] {assistant_reply}")

        return assistant_reply
