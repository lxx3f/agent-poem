FROM python:3.10-slim-bookworm

# 1. 基础环境
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

WORKDIR /app

# 2. 系统依赖（Milvus / numpy / faiss 常见需求）
RUN rm -rf /etc/apt/sources.list /etc/apt/sources.list.d/* && \
    # 第二步：写入国内阿里云的bookworm完整源（包含安全更新，国内访问稳定）
    echo "deb [trusted=yes] http://mirrors.aliyun.com/debian bookworm main non-free contrib" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://mirrors.aliyun.com/debian-security bookworm-security main non-free contrib" >> /etc/apt/sources.list && \
    apt-get -o Acquire::Check-Valid-Until=false -o APT::Get::AllowUnauthenticated=true update && \
    # 安装依赖，--no-install-recommends减小镜像体积
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && \
    # 清理缓存，减少镜像大小
    rm -rf /var/lib/apt/lists/*

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

