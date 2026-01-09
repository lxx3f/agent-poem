from fastapi import APIRouter, Depends
from typing import List, cast

from app.core.jwt import get_current_user
from app.core.response import StandardResponse, success_response, error_response
from app.services.message_service import MessageService
from app.schemas.conversation import (
    MessageCreateRequest,
    MessageItem,
)
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/message", tags=["Message"])


@router.get("/{message_id}", response_model=StandardResponse[MessageItem])
def get_message(
        message_id: int,
        current_user=Depends(get_current_user),
):
    '''
    获取单条消息详情
    
    :param message_id: 消息ID
    :type message_id: int
    :param current_user: 当前用户
    '''
    service = MessageService()
    message = service.get_message_by_id(
        message_id=message_id,
        user_id=current_user["id"],
    )
    return success_response(message)
