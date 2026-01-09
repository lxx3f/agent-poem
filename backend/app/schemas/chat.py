from pydantic import BaseModel, Field


class ChatCompleteRequest(BaseModel):
    conversation_id: int = Field(..., description="会话ID")
    message: str = Field(..., description="用户输入内容")


class ChatCompleteResponse(BaseModel):
    message_id: int
    role: str
    content: str
