FROM python:3.10-slim

# 1. 基础环境
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

WORKDIR /app

# 2. 系统依赖（Milvus / numpy / faiss 常见需求）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. 安装 Python 依赖（利用 Docker cache）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制代码
COPY app ./app
COPY scripts ./scripts
COPY ../.env .env

# 5. 创建日志目录
RUN mkdir -p /app/logs

# 6. 暴露端口（和 main.py 中一致）
EXPOSE 8000

# 7. 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

