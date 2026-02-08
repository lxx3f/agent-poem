from typing import Optional, Literal, List
from datetime import datetime
from pydantic import BaseModel, Field
import json

RoleType = Literal["user", "assistant", "system"]


class ConversationCreateRequest(BaseModel):
    title: str = Field("新对话", description="会话标题")
    agent_id: int
    memory_data: Optional[dict] = None  # 新增的短期记忆数据字段


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
    memory_data: Optional[dict] = None  # 新增的短期记忆数据字段
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