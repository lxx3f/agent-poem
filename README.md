# 诗云 - 基于大语言模型的诗词智能问答与互动平台

"诗云"是一个基于大语言模型（LLM）和向量检索技术的诗词智能问答与互动平台，旨在通过自然语言理解用户意图，精准匹配并返回古典诗词内容，并支持飞花令、诗词接龙等传统文化玩法。

## 项目特色

- **语义理解**：基于大语言模型和RAG（检索增强生成）技术，能够理解用户的自然语言意图，解决传统关键词搜索难以理解语义的问题
- **智能匹配**：使用向量数据库Milvus进行高维嵌入相似度检索，实现精准的诗词匹配
- **多样化玩法**：支持飞花令、诗词接龙等多类型Agent玩法，丰富诗词学习体验
- **多LLM支持**：支持OpenAI、DeepSeek、Qwen等多种大语言模型
- **模块化设计**：采用模块化Agent设计，易于扩展新功能

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
└── docker-compose.yml     # 服务编排配置
```

## 技术栈

- **前端**: Vue3 + TypeScript + Vite
- **后端**: Python + FastAPI
- **大语言模型**: OpenAI GPT、阿里通义千问、DeepSeek等
- **数据库**: MySQL（主数据存储）
- **向量数据库**: Milvus（语义向量检索）
- **缓存**: Redis
- **构建与部署**: Docker + docker-compose

## 功能模块

### 1. 智能检索
- 根据用户自然语言描述进行语义匹配检索
- 支持按主题、情感、场景等维度搜索诗词

### 2. 互动游戏
- 飞花令：基于AI的智能飞花令游戏
- 诗词接龙：支持多种接龙规则的游戏模式

### 3. 诗词问答
- 诗词内容咨询与解释
- 诗人背景知识问答
- 诗词创作技巧指导

### 4. 用户系统
- 用户注册与登录
- 会话历史记录

## 部署说明

### 环境要求

- Docker 20.10+
- Docker Compose v2+
- 至少8GB内存（推荐16GB）

### 快速启动

1. **克隆项目**



2. **配置环境变量**

复制并编辑 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入必要的配置项：
- 数据库配置
- LLM API KEY


3. **启动服务**

```bash
# 构建并启动所有服务
docker-compose up -d --build
```

4. **初始化数据**

```bash
# 项目根目录下运行
# 运行数据导入脚本（此步骤可能需要较长时间）
python /backend/scripts/import_data.py
```

### 服务访问

- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **Milvus控制台**: http://localhost:9091
- **MinIO控制台**: http://localhost:9001
- **phpMyAdmin**: http://localhost:8081

## 开发说明

### 本地开发

1. **后端开发**

```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动后端服务
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **前端开发**

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 数据库结构

项目使用MySQL存储结构化数据，Milvus存储诗词向量数据：

- **用户表**: 存储用户信息
- **会话表**: 存储对话会话
- **消息表**: 存储对话消息记录
- **诗词表**: 存储诗词原文、作者、朝代等信息
- **向量库**: 存储诗词向量表示，用于语义检索

