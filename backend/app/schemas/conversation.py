from typing import Optional, Literal, List
from datetime import datetime
from pydantic import BaseModel, Field

RoleType = Literal["user", "assistant", "system"]


class BaseUserRequest(BaseModel):
    pass


class ConversationCreateRequest(BaseUserRequest):
    title: str = Field("新对话", description="会话标题")


class ConversationListRequest(BaseUserRequest):
    limit: int = 20
    offset: int = 0


class ConversationItem(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime


class MessageItem(BaseModel):
    id: int
    role: RoleType
    content: str
    created_at: datetime


class MessageListRequest(BaseUserRequest):
    conversation_id: int
    limit: int = 50


class MessageListResponse(BaseUserRequest):
    conversation_id: int
    total: int = 50
    messages: List[MessageItem]


class MessageCreateRequest(BaseUserRequest):
    conversation_id: int
    role: RoleType
    content: str
