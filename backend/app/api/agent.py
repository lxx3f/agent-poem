from fastapi import APIRouter, Depends
from typing import List, cast

from backend.app.core.jwt import get_current_user
from backend.app.core.response import StandardResponse, success_response, error_response
from backend.app.services.conversation_service import ConversationService
from backend.app.services.message_service import MessageService
from backend.app.services.agent_service import AgentService
from backend.app.schemas.agent import (AgentListRequest, AgentItem,
                                       AgentRunRequest, AgentListResponse)

router = APIRouter(prefix="/api/agent", tags=["Agent"])


@router.get("/list", response_model=StandardResponse[AgentListResponse])
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


@router.post("/{agent_id}/run", response_model=StandardResponse[str])
def run_agent(
        agent_id: int,
        req: AgentRunRequest,
        current_user=Depends(get_current_user),
):
    agent_service = AgentService()
    reply = agent_service.run_agent(
        agent_id=agent_id,
        user_input=req.user_input,
        conversation_id=req.conversation_id,
        user_id=current_user["id"],
        workflow=req.workflow,
    )
    return success_response(reply)
