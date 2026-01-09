from pymilvus import Collection, connections
from typing import List, Any, cast
from app.core.config import settings
from app.core.exceptions import BusinessException


class MilvusService:

    def __init__(self) -> None:
        self._connect()
        self.collection = Collection(settings.MILVUS_COLLECTION)

    def _connect(self) -> None:
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
        )

    def search(self, vector: list[float], limit: int = 5) -> list[int]:
        """
        向量检索，返回 poetry_id 列表
        """
        results = self.collection.search(data=[vector],
                                         anns_field="embedding",
                                         param={
                                             "metric_type": "IP",
                                             "params": {
                                                 "nprobe": 10
                                             }
                                         },
                                         limit=limit,
                                         output_fields=["poetry_id"])

        poetry_ids: List[int] = []
        hits = cast(List[Any], results)
        for hit in hits[0]:
            pid = hit.get("poetry_id") if hasattr(hit, "get") else None
            if pid is not None:
                poetry_ids.append(pid)

        return poetry_ids
