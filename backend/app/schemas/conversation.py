from typing import Optional, Literal, List
from datetime import datetime
from pydantic import BaseModel, Field

RoleType = Literal["user", "assistant", "system"]


class ConversationCreateRequest(BaseModel):
    title: str = Field("新对话", description="会话标题")
    agent_id: int


class ConversationCreateResponse(BaseModel):
    conversation_id: int


class ConversationListRequest(BaseModel):
    agent_id: int
    limit: int = 20
    offset: int = 0


class ConversationItem(BaseModel):
    id: int
    agent_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    conversations: List[ConversationItem]
    total: int


class MessageItem(BaseModel):
    id: int
    role: RoleType
    content: str
    created_at: datetime


class MessageListRequest(BaseModel):
    conversation_id: int
    limit: int = 50


class MessageListResponse(BaseModel):
    conversation_id: int
    total: int = 50
    messages: List[MessageItem]
