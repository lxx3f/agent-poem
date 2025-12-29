from fastapi import APIRouter, Depends
from typing import List, cast

from backend.app.core.jwt import get_current_user
from backend.app.core.response import StandardResponse, success_response, error_response
from backend.app.services.message_service import MessageService
from backend.app.schemas.conversation import (
    MessageCreateRequest,
    MessageItem,
)
from backend.app.llm.llm_service import get_llm_service

router = APIRouter(prefix="/api/message", tags=["Message"])


@router.get("/{message_id}", response_model=StandardResponse[MessageItem])
def get_message(
        message_id: int,
        current_user=Depends(get_current_user),
):
    '''
    获取单条消息详情
    
    :param message_id: 说明
    :type message_id: int
    :param current_user: 说明
    '''
    service = MessageService()
    message = service.get_message_by_id(
        message_id=message_id,
        user_id=current_user["id"],
    )
    return success_response(message)


@router.post("/create", response_model=StandardResponse[int])
def send_message(
        req: MessageCreateRequest,
        current_user=Depends(get_current_user),
):
    '''
    发送消息到某个会话，调用chat工具处理消息，返回响应消息的 ID
    
    :param req: 说明
    :type req: MessageCreateRequest
    :param current_user: 说明
    '''
    service = MessageService()
    user_message_id = service.create_message(
        conversation_id=req.conversation_id,
        user_id=current_user["id"],
        role=req.role,
        status="done",
        content=req.content,
    )
    llm_message_id = service.create_message(
        conversation_id=req.conversation_id,
        user_id=current_user["id"],
        role="assistant",
        status="pending",
        content="",
    )
    llm_servive = get_llm_service()
    llm_servive.process_message(
        message_id=user_message_id,
        response_message_id=llm_message_id,
        conversation_id=req.conversation_id,
        user_id=current_user["id"],
    )

    return success_response(llm_message_id)
