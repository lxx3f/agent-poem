from typing import List, Dict, Any, Optional, Literal

from backend.app.core.exceptions import BusinessException
from backend.app.services.mysql_service import MySQLService
from backend.app.workflows.poetry_game import PoetryGameWorkflow
from backend.app.workflows.rag_chat import RagChatWorkflow


class AgentService:
    '''
    Agent 服务
    '''

    def __init__(self) -> None:
        self.mysql_service = MySQLService()

    # =====================
    # Agent 相关
    # =====================
    def get_agent(self, agent_id: int) -> Dict[str, Any]:
        '''
        根据 ID 获取 Agent 详情
        
        :param agent_id: agent ID
        :type agent_id: int
        :return: agent 详情
        :rtype: Optional[Dict[str, Any]]
        '''
        return self.mysql_service.get_agent_by_id(agent_id)

    def list_agents(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        '''
        获取所有 Agent 列表
        
        :param limit: 限制数量
        :type limit: int
        :return: 所有 Agent 列表
        :rtype: List[Dict[str, Any]]
        '''
        return self.mysql_service.get_agents(limit)

    def run_agent(
        self,
        agent_id: int,
        user_input: str,
        conversation_id: int,
        user_id: int,
        workflow: Literal["poetry_game", "rag_chat"] = "rag_chat",
    ) -> str:
        '''
        运行 Agent
        
        :param agent_id: agent ID
        :type agent_id: int
        :param user_input: 用户输入
        :type user_input: str
        :param conversation_id: 聊天会话 ID
        :type conversation_id: int
        :param user_id: 用户 ID
        :type user_id: int
        :param workflow: 工作流名称
        :type workflow: Literal["poetry_game", "rag_chat"]
        '''

        # 调用 workflow
        if workflow == "poetry_game":
            return PoetryGameWorkflow().run(
                conversation_id=conversation_id,
                user_id=user_id,
                user_input=user_input,
            )
        elif workflow == "rag_chat":

            return RagChatWorkflow().run(
                conversation_id=conversation_id,
                user_id=user_id,
                user_input=user_input,
            )
        else:
            raise BusinessException("无效的工作流")
