from pymilvus import (Collection, connections, FieldSchema, CollectionSchema,
                      DataType, utility)
from typing import List, Any, cast
from app.core.config import settings
from app.core.exceptions import BusinessException


class MilvusService:

    def __init__(self) -> None:
        self._connect()

        if utility.has_collection(settings.MILVUS_COLLECTION):
            self.collection = Collection(settings.MILVUS_COLLECTION)
            return None

        fields = [
            FieldSchema(
                name="poetry_id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=False,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=settings.EMBEDDING_DIM,
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Poetry semantic embedding",
        )

        collection = Collection(
            name=settings.MILVUS_COLLECTION,
            schema=schema,
        )

        res = collection.create_index(
            field_name="embedding",
            index_params={
                "index_type": "IVF_FLAT",
                "metric_type": "IP",
                "params": {
                    "nlist": 1024
                },
            },
        )

        self.collection = collection

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
