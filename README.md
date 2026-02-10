# 诗云 - 基于大语言模型的诗词智能问答与互动平台

"诗云"是一个基于大语言模型（LLM）和向量检索技术的诗词智能问答与互动平台，旨在通过自然语言理解用户意图，精准匹配并返回古典诗词内容，并支持飞花令、诗词接龙等传统文化玩法。

## 项目特色

- **语义理解**：基于大语言模型和RAG（检索增强生成）技术，能够理解用户的自然语言意图，解决传统关键词搜索难以理解语义的问题
- **智能匹配**：使用向量数据库Milvus进行高维嵌入相似度检索，实现精准的诗词匹配
- **多样化玩法**：支持飞花令、诗词接龙等多类型Agent玩法，丰富诗词学习体验
- **多LLM支持**：支持OpenAI、DeepSeek、Qwen等多种大语言模型
- **模块化设计**：采用模块化Agent设计，易于扩展新功能
- **现代化架构**：基于Vue3 + FastAPI的全栈开发，支持Docker容器化部署

## 架构概览

```
.
├── backend                 # 后端服务 (FastAPI)
│   ├── app
│   │   ├── agents         # 不同功能Agent实现
│   │   ├── api            # RESTful路由定义
│   │   ├── core           # 配置、异常、JWT工具等
│   │   ├── llm            # 封装多种LLM客户端
│   │   ├── rag            # 检索增强生成核心逻辑
│   │   ├── schemas        # Pydantic模型定义
│   │   ├── services       # 业务逻辑封装
│   │   └── workflows      # 复杂交互流程控制
│   └── scripts            # 数据导入和测试脚本
├── database               # 数据库和诗词数据集
│   ├── chinese-gushiwen   # 中文古诗文数据
│   └── init.sql           # 数据库初始化脚本
├── frontend               # 前端 (Vue3 + Vite)
│   ├── src
│   │   ├── api            # API接口定义
│   │   ├── components     # Vue组件
│   │   ├── router         # 路由配置
│   │   ├── stores         # 状态管理
│   │   ├── types          # 类型定义
│   │   └── views          # 页面视图
│   └── public             # 静态资源
├── docs                   # 项目文档
│   └── api               # API接口文档
└── docker-compose.yml     # 服务编排配置
```

## 技术栈

### 前端
- **框架**: Vue 3.5.24 + TypeScript
- **构建工具**: Vite 7.2.4
- **UI组件库**: Element Plus 2.13.1
- **状态管理**: Pinia 3.0.4
- **路由**: Vue Router 4.6.4
- **HTTP客户端**: Axios 1.13.2

### 后端
- **框架**: FastAPI 0.128.0
- **Python版本**: 3.9+
- **数据库**: MySQL 8.0
- **向量数据库**: Milvus 2.3.0
- **缓存**: Redis 7.0
- **LLM支持**: Qwen, Ollama
- **ORM**: PyMySQL 1.1.2
- **向量检索**: PyMilvus 2.6.5

### 部署与运维
- **容器化**: Docker + Docker Compose

## 功能模块

### 1. 智能检索
- 根据用户自然语言描述进行语义匹配检索
- 支持按主题、情感、场景等维度搜索诗词
- 基于Milvus向量数据库的高精度语义匹配

### 2. 互动游戏
- **飞花令**：基于AI的智能飞花令游戏
- **诗词接龙**：支持多种接龙规则的游戏模式
- **诗词问答**：智能诗词解释和背景介绍

### 3. 用户系统
- 用户注册与登录（JWT认证）
- 会话历史记录管理
- 个性化记忆存储

### 4. Agent智能体
- 模块化Agent设计，支持插件式扩展
- 预置多种诗词相关Agent
- 支持自定义Prompt

## 部署说明

### 环境要求

- Docker 20.10+
- Docker Compose v2+
- 至少8GB内存（推荐16GB）


### 快速启动

1. **克隆项目**
```bash
git clone https://github.com/lxx3f/agent-poem.git
cd agent-poem
```

2. **配置环境变量**

复制并编辑 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，主要配置项包括：
```bash
# 数据库配置
MYSQL_PASSWORD=your_secure_password
MYSQL_ROOT_PASSWORD=your_secure_root_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# LLM配置（选择其一）
# 阿里云Qwen配置
QWEN_API_KEY=sk-your-dashscope-api-key-here
QWEN_MODEL=qwen-max

# 或使用本地Ollama（默认）
LLM_PROVIDER=ollama
```

3. **启动服务**
```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

4. **初始化数据**
```bash
# 本地运行数据导入脚本（首次部署必须执行）
python scripts/import_data.py
```

### 服务访问

- **前端应用**: http://localhost:8080
- **后端API文档**: http://localhost:8000/docs
- **Milvus控制台**: http://localhost:9091
- **MinIO控制台**: http://localhost:9001
- **phpMyAdmin**: http://localhost:8081
- **Ollama API**: http://localhost:11434

## 开发说明

### 本地开发环境

#### 后端开发
```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 数据库结构

项目使用以下数据库服务：

- **MySQL**: 存储用户信息、会话记录、诗词元数据等结构化数据
- **Milvus**: 存储诗词向量表示，用于语义检索
- **Redis**: 缓存热点数据和会话状态
- **MinIO**: 对象存储（Milvus依赖）

主要数据表包括：
- `users`: 用户信息表
- `agents`: AI智能体配置表
- `conversations`: 对话会话表
- `messages`: 消息记录表
- `writer`: 诗词作者表
- `poetry`: 诗词内容表
- `sentence`: 诗句表

### API文档

详细的API接口文档请参考 [docs/api/](./docs/api/) 目录：
- [API接口文档](./docs/api/API接口文档.md) - 完整的RESTful API说明
- [API索引](./docs/api/README.md) - API文档导航

## 项目文档

- [数据库设计](./docs/数据库设计.md) - 详细的数据表结构说明
- [模块设计](./docs/模块和层次设计.md) - 系统架构和模块划分
- [API文档](./docs/api/) - 完整的API接口文档
