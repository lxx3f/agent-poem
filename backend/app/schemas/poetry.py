from pydantic import BaseModel
from typing import Literal, Optional, List


class PoetrySearchRequest(BaseModel):
    query: str
    search_type: Literal["keyword", "vector", "hybrid"] = "hybrid"
    top_k: int = 5


class PoetrySearchItem(BaseModel):
    id: int
    title: str
    dynasty: str
    writer: str
    content: str
    score: Optional[float] = None


class PoetrySearchResponse(BaseModel):
    total: int
    items: List[PoetrySearchItem]
