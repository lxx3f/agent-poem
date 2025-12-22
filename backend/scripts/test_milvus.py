from pymilvus import connections, utility

# 连接Milvus
connections.connect(
    alias="default",
    host="127.0.0.1",  # 本地地址
    port="19530")

# 验证连接（打印Milvus版本）
print("Milvus版本：", utility.get_server_version())
# 关闭连接
connections.disconnect("default")
