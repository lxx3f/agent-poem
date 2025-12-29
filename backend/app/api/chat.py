from fastapi import APIRouter, Depends
from backend.app.core.response import success_response
from backend.app.core.jwt import get_current_user
from backend.app.schemas.chat import (
    ChatCompleteRequest,
    ChatCompleteResponse,
)
from backend.app.services.conversation_service import ConversationService
from backend.app.llm.llm_service import LLMService, get_llm_service
from backend.app.llm.types import LLMMessage
from typing import cast

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/complete")
def chat_complete(
        req: ChatCompleteRequest,
        current_user=Depends(get_current_user),
):
    user_id = current_user["id"]

    conversation_service = ConversationService()
    llm_service = get_llm_service()

    conversation_service.add_message(
        user_id=user_id,
        conversation_id=req.conversation_id,
        role="user",
        content=req.message,
    )

    history_messages = conversation_service.list_messages(
        user_id=user_id,
        conversation_id=req.conversation_id,
        limit=10,
    )

    # 调用 LLM
    assistant_content = llm_service.chat(
        cast(list[LLMMessage], history_messages))

    # 插入 assistant message
    assistant_message_id = conversation_service.add_message(
        user_id=user_id,
        conversation_id=req.conversation_id,
        role="assistant",
        content=assistant_content,
    )

    # 返回
    return success_response(
        ChatCompleteResponse(
            message_id=assistant_message_id,
            role="assistant",
            content=assistant_content,
        ))
