from typing import List

from app.rag.base import RAGContext
from app.services.embedding_service import Embedding_service
from app.services.milvus_service import MilvusService


class PoetryRAG(RAGContext):

    def __init__(self):
        self.embedding = Embedding_service()
        self.vector_db = MilvusService()

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        vector = self.embedding.get_embedding(query)
        results = self.vector_db.search(vector, limit=top_k)
        # TODO 检索结果处理
        return ["" for item in results]
