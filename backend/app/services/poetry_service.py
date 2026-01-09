from typing import Any, Dict, List, Literal

from backend.app.services.embedding_service import Embedding_service
from backend.app.services.milvus_service import MilvusService
from backend.app.services.mysql_service import MySQLService
from backend.app.core.exceptions import BusinessException

SearchType = Literal["keyword", "vector", "hybrid"]


class PoetryService:

    def __init__(
            self,
            embedding_service: Embedding_service = Embedding_service(),
            milvus_service: MilvusService = MilvusService(),
            mysql_service: MySQLService = MySQLService(),
    ):
        self.embedding_service = embedding_service
        self.milvus_service = milvus_service
        self.mysql_service = mysql_service

    def search(
        self,
        query: str,
        search_type: SearchType = "hybrid",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        '''
        搜索古诗词
        
        :param query: 搜索关键词
        :type query: str
        :param search_type: 搜索类型："keyword", "vector", "hybrid"
        :type search_type: SearchType
        :param top_k: 返回结果数量
        :type top_k: int
        :return: 搜索结果列表
        :rtype: List[Dict[str, Any]]
        '''
        if search_type not in ("keyword", "vector", "hybrid"):
            raise BusinessException("Invalid search type")

        poetry_ids: List[int] = []

        # 1. 关键词搜索
        if search_type in ("keyword", "hybrid"):
            keyword_ids = self.mysql_service.search_poetry_ids_by_keyword(
                keyword=query,
                limit=top_k,
            )
            poetry_ids.extend(keyword_ids)

        # 2. 向量搜索
        if search_type in ("vector", "hybrid"):
            vector = self.embedding_service.get_embedding(query)
            vector_ids = self.milvus_service.search(
                vector=vector,
                limit=top_k,
            )
            poetry_ids.extend(vector_ids)

        # 3. 去重 + 截断
        poetry_ids = list(dict.fromkeys(poetry_ids))[:top_k]

        if not poetry_ids:
            return []

        # 4. 查详情
        rows = self.mysql_service.get_poetry_by_ids(poetry_ids)

        # 测试
        # for row in rows:
        #     print(row.keys())

        # 5. 组装
        result: List[Dict[str, Any]] = []

        for row in rows:
            pid = row["id"]
            result.append({
                'id': row["id"],
                "title": row["title"],
                "dynasty": row["dynasty"],
                "writer": row["name"],
                "content": row["content"],
            })

        return result
