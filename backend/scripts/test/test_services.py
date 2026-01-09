"""
测试 MilvusService 的向量检索功能，以及 embedding 服务的向量生成。
"""

from pymilvus import Collection, connections
from app.services.milvus_service import MilvusService

# 假设有一个 embedding_service.py，提供 get_embedding(text: str) -> list[float]
from app.services.embedding_service import Embedding_service


def main():
    # 1. 连接 Milvus
    connections.connect(alias="default", host="localhost", port="19530")

    # 2. 获取 Collection（假设 collection 名为 "poem_vectors"）
    collection = Collection("poem_vectors")

    # 3. 实例化 MilvusService
    milvus_service = MilvusService(collection)

    # 4. 测试 embedding 服务
    embedding_service = Embedding_service()
    test_text = "春日宴饮"
    vector = embedding_service.get_embedding(test_text)
    if vector == None:
        vector = []
    print(f"Embedding 向量: {vector[:5]} ... 共 {len(vector)} 维")

    # 5. 测试 Milvus 检索
    poetry_ids = milvus_service.search(vector, limit=5)
    print("检索到的 poetry_id:", poetry_ids)

    # 6. 断言结果（可选）
    assert isinstance(poetry_ids, list)
    assert all(isinstance(pid, int) or pid is None for pid in poetry_ids)

    print("Milvus & embedding 服务测试通过！")


if __name__ == "__main__":
    main()
