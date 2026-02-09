from fastapi import APIRouter, Depends
from typing import List, cast

from app.core.jwt import get_current_user
from app.core.response import StandardResponse, success_response, error_response
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.agent_service import AgentService
from app.schemas.agent import (AgentListRequest, AgentItem, AgentRunRequest,
                               AgentListResponse, AgentRunResponse)
from app.schemas.agent import (AgentUpdateSystemPromptResponse,
                               AgentUpdateSystemPromptRequest)

router = APIRouter(prefix="/api/agent", tags=["Agent"])


@router.post("/list", response_model=StandardResponse[AgentListResponse])
def list_agents(
        req: AgentListRequest,
        current_user=Depends(get_current_user),
):
    '''
    列出所有agents
    
    :param req: 请求体
    :type req: AgentListRequest
    :param current_user: 当前用户
    '''
    agent_service = AgentService()
    agents = agent_service.list_agents(limit=req.limit)
    agents = [
        AgentItem.model_validate(agent, from_attributes=True)
        for agent in agents
    ]
    return success_response(
        AgentListResponse(total=len(agents), agents=(agents)))


@router.get("/{agent_id}", response_model=StandardResponse[AgentItem])
def get_agent(
        agent_id: int,
        current_user=Depends(get_current_user),
):
    '''
    获取某个agent详情
    
    :param agent_id: agent ID
    :type agent_id: int
    :param current_user: 当前用户
    '''
    agent_service = AgentService()
    agent = agent_service.get_agent(agent_id=agent_id)
    agent = AgentItem.model_validate(agent, from_attributes=True)
    return success_response(agent)


@router.post("/{agent_id}/run",
             response_model=StandardResponse[AgentRunResponse])
def run_agent(
        agent_id: int,
        req: AgentRunRequest,
        current_user=Depends(get_current_user),
):
    '''
    运行某个agent
    
    :param agent_id: agent ID
    :type agent_id: int
    :param req: 运行参数
    :type req: AgentRunRequest
    :param current_user: 当前用户
    '''
    agent_service = AgentService()
    agent_service.run_agent(
        agent_id=agent_id,
        user_input=req.user_input,
        conversation_id=req.conversation_id,
        user_id=current_user["id"],
    )
    return success_response(AgentRunResponse(message="运行成功"))


@router.post("/{agent_id}/update_system_prompt",
             response_model=StandardResponse[AgentUpdateSystemPromptResponse])
def update_agent_system_prompt(
        agent_id: int,
        req: AgentUpdateSystemPromptRequest,
        current_user=Depends(get_current_user),
):
    '''
    更新agent的system_prompt(游戏规则提示词)
    '''
    agent_service = AgentService()
    affected_rows = agent_service.update_agent_system_prompt(
        agent_id=agent_id, system_prompt=req.system_prompt)
    return success_response(
        AgentUpdateSystemPromptResponse(
            message=f"成功更新agent {agent_id}的system_prompt，影响{affected_rows}行",
            agent_id=agent_id))
