from typing import Optional, Literal, List
from datetime import datetime
from pydantic import BaseModel, Field


class AgentItem(BaseModel):
    id: int
    name: str
    code: str
    description: str
    workflow: str
    system_prompt: str
    parameters: Optional[str]
    llm_config: Optional[str]
    is_active: bool


class AgentListRequest(BaseModel):
    limit: int = 50


class AgentListResponse(BaseModel):
    total: int
    agents: List[AgentItem]


class AgentRunRequest(BaseModel):
    user_input: str
    conversation_id: int
    user_id: int
    workflow: Literal["poetry_game", "rag_chat"] = "rag_chat"
    history_limit: int = 10
