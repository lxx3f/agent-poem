from typing import List, Any

from backend.app.rag.poetry_rag import PoetryRAG


class RAGService:

    def __init__(self) -> None:
        self.poetryRag = PoetryRAG()

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        return self.poetryRag.retrieve(query, top_k)
