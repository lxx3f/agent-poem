from fastapi import APIRouter, Depends
from typing import List, cast

from app.core.jwt import get_current_user
from app.core.response import StandardResponse, success_response, error_response
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationListRequest,
    ConversationItem,
    MessageListRequest,
    MessageListResponse,
    MessageItem,
)

router = APIRouter(prefix="/api/conversation", tags=["Conversation"])


@router.post("/create", response_model=StandardResponse[int])
def create_conversation(
        req: ConversationCreateRequest,
        current_user=Depends(get_current_user),
):
    '''
    创建新会话,返回会话 ID
    
    :param req: 请求体
    :type req: ConversationCreateRequest
    :param current_user: 当前用户
    '''
    service = ConversationService()
    conversation_id = service.create_conversation(
        user_id=current_user["id"],
        agent_id=req.agent_id,
        title=req.title,
    )
    return success_response(conversation_id)


@router.post("/{conversation_id}",
             response_model=StandardResponse[MessageListResponse])
def list_messages_by_conversation(
        conversation_id: int,
        req: MessageListRequest,
        current_user=Depends(get_current_user),
):
    '''
    列出会话的消息列表
    
    :param req: 请求体
    :type req: MessageListRequest
    :param current_user: 当前用户
    '''
    service = MessageService()
    messages = service.get_messages_by_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        limit=req.limit,
    )
    total = len(messages)
    response = MessageListResponse(
        conversation_id=conversation_id,
        total=total,
        messages=[MessageItem(**msg) for msg in messages],
    )
    return success_response(response)


@router.post("/list", response_model=StandardResponse[list[ConversationItem]])
def list_conversations(
        req: ConversationListRequest,
        current_user=Depends(get_current_user),
):
    '''
    列出用户的会话列表
    
    :param req: 请求体
    :type req: ConversationListRequest
    :param current_user: 当前用户
    '''
    service = ConversationService()
    items = service.list_conversations(
        user_id=current_user["id"],
        agent_id=req.agent_id,
        limit=req.limit,
        offset=req.offset,
    )
    return success_response(items)


@router.delete("/{conversation_id}", response_model=StandardResponse[None])
def delete_conversation(
        conversation_id: int,
        current_user=Depends(get_current_user),
):
    '''
    删除某个会话
    
    :param conversation_id: 会话 ID
    :type conversation_id: int
    :param current_user: 当前用户
    '''
    service = ConversationService()
    service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"],
    )
    return success_response(None)
