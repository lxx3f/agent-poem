from fastapi import APIRouter, Depends

from backend.app.core.jwt import get_current_user
from backend.app.core.response import StandardResponse, success_response, error_response
from backend.app.services.conversation_service import ConversationService
from backend.app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationListRequest,
    ConversationItem,
    MessageListRequest,
    MessageCreateRequest,
    MessageItem,
)

router = APIRouter(prefix="/api/conversation", tags=["Conversation"])


@router.post("/create", response_model=StandardResponse[int])
def create_conversation(
        req: ConversationCreateRequest,
        current_user=Depends(get_current_user),
):
    service = ConversationService()
    conversation_id = service.create_conversation(
        user_id=current_user["id"],
        title=req.title,
    )
    return success_response(conversation_id)


@router.post("/list", response_model=StandardResponse[list[ConversationItem]])
def list_conversations(
        req: ConversationListRequest,
        current_user=Depends(get_current_user),
):
    service = ConversationService()
    items = service.list_conversations(
        user_id=current_user["id"],
        limit=req.limit,
        offset=req.offset,
    )
    return success_response(items)


@router.post("/messages", response_model=StandardResponse[list[MessageItem]])
def list_messages(
        req: MessageListRequest,
        current_user=Depends(get_current_user),
):
    service = ConversationService()
    messages = service.list_messages(
        conversation_id=req.conversation_id,
        user_id=current_user["id"],
        limit=req.limit,
    )
    return success_response(messages)


@router.post("/add_message", response_model=StandardResponse[int])
def add_message(
        req: MessageCreateRequest,
        current_user=Depends(get_current_user),
):
    service = ConversationService()
    message_id = service.add_message(
        conversation_id=req.conversation_id,
        user_id=current_user["id"],
        role=req.role,
        content=req.content,
    )
    return success_response(message_id)
