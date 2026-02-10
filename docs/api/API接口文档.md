# API设计文档

## 统一响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

字段说明:

| 字段名 | 类型 | 说明 |
| ---- | --- | ---- |
| code | integer | 状态码，200 表示成功 |
| message | string | 状态说明 |
| data | json | 业务数据 |

设计原则：
- service层写处理逻辑，返回dict，api层封装
- 所有接口均遵循RESTful风格
- 认证接口除外，其余接口都需要在Header中携带JWT Token: `Authorization: Bearer <token>`

## 模块划分

## 1. 认证接口 (Auth API)

### 1.1 用户注册
- **接口路径**: `POST /api/auth/register`
- **功能**: 注册新用户
- **请求体**:
  ```json
  {
    "email": "string",
    "password": "string",
    "nickname": "string"
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "message": "注册成功",
    "data": {
      "id": 123,
      "email": "user@example.com",
      "nickname": "用户名"
    }
  }
  ```

### 1.2 用户登录
- **接口路径**: `POST /api/auth/login`
- **功能**: 用户登录
- **请求体**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "Bearer"
    }
  }
  ```

### 1.3 获取当前用户信息
- **接口路径**: `GET /api/auth/me`
- **功能**: 获取当前登录用户信息
- **认证**: 需要在Header中携带JWT Token
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "id": 123,
      "email": "user@example.com",
      "nickname": "用户名",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  }
  ```

### 1.4 更新用户信息
- **接口路径**: `POST /api/auth/update`
- **功能**: 更新用户昵称
- **认证**: 需要在Header中携带JWT Token
- **请求体**:
  ```json
  {
    "nickname": "string"
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": null
  }
  ```

## 2. 智能体接口 (Agent API)

### 2.1 列出所有智能体
- **接口路径**: `POST /api/agent/list`
- **功能**: 获取所有可用的智能体列表
- **认证**: 需要在Header中携带JWT Token
- **请求体**:
  ```json
  {
    "limit": 50
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "total": 3,
      "agents": [
        {
          "id": 1,
          "name": "诗词问答助手",
          "code": "poetry_qa",
          "description": "专业的诗词问答智能体",
          "workflow_key": "rag_chat",
          "system_prompt": "你是诗词专家...",
          "parameters": "{\"temperature\": 0.7}",
          "llm_config": "{\"model\": \"qwen-plus\"}",
          "is_active": true,
          "created_at": "2024-01-01T00:00:00",
          "updated_at": "2024-01-01T00:00:00"
        }
      ]
    }
  }
  ```

### 2.2 获取智能体详情
- **接口路径**: `GET /api/agent/{agent_id}`
- **功能**: 获取特定智能体的详细信息
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `agent_id`: 智能体ID
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "id": 1,
      "name": "诗词问答助手",
      "code": "poetry_qa",
      "description": "专业的诗词问答智能体",
      "workflow_key": "rag_chat",
      "system_prompt": "你是诗词专家...",
      "parameters": "{\"temperature\": 0.7}",
      "llm_config": "{\"model\": \"qwen-plus\"}",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  }
  ```

### 2.3 运行智能体
- **接口路径**: `POST /api/agent/{agent_id}/run`
- **功能**: 运行特定智能体处理用户输入
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `agent_id`: 智能体ID
- **请求体**:
  ```json
  {
    "user_input": "string",      // 用户输入内容
    "conversation_id": 123,      // 会话ID
    "history_limit": 10          // 历史消息限制数量，默认10
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "message": "运行成功"
    }
  }
  ```

### 2.4 更新智能体系统提示词
- **接口路径**: `POST /api/agent/{agent_id}/update_system_prompt`
- **功能**: 更新智能体的system_prompt(游戏规则提示词)
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `agent_id`: 智能体ID
- **请求体**:
  ```json
  {
    "system_prompt": "string"    // 新的系统提示词，长度1-10000字符
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "message": "成功更新agent 1的system_prompt，影响1行",
      "agent_id": 1
    }
  }
  ```

## 3. 会话接口 (Conversation API)

### 3.1 创建会话
- **接口路径**: `POST /api/conversation/create`
- **功能**: 创建新会话
- **认证**: 需要在Header中携带JWT Token
- **请求体**:
  ```json
  {
    "agent_id": 1,               // 智能体ID
    "title": "新对话",           // 会话标题
    "memory_data": {}            // 可选的短期记忆数据
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "conversation_id": 123
    }
  }
  ```

### 3.2 列出会话消息
- **接口路径**: `POST /api/conversation/{conversation_id}/messages`
- **功能**: 获取指定会话的消息列表
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `conversation_id`: 会话ID
- **请求体**:
  ```json
  {
    "limit": 50                  // 限制返回数量，默认50
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "conversation_id": 123,
      "total": 10,
      "messages": [
        {
          "id": 456,
          "role": "user",        // user, assistant, system
          "content": "你好",
          "created_at": "2024-01-01T00:00:00"
        }
      ]
    }
  }
  ```

### 3.3 列出用户会话
- **接口路径**: `POST /api/conversation/list`
- **功能**: 获取用户的会话列表
- **认证**: 需要在Header中携带JWT Token
- **请求体**:
  ```json
  {
    "agent_id": 1,               // 可选的智能体ID筛选
    "limit": 20,                 // 限制返回数量，默认20
    "offset": 0                  // 偏移量，默认0
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "total": 15,
      "conversations": [
        {
          "id": 123,
          "agent_id": 1,
          "title": "诗词讨论",
          "memory_data": {},       // 短期记忆数据
          "created_at": "2024-01-01T00:00:00",
          "updated_at": "2024-01-01T00:00:00"
        }
      ]
    }
  }
  ```

### 3.4 删除会话
- **接口路径**: `DELETE /api/conversation/{conversation_id}`
- **功能**: 删除指定会话
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `conversation_id`: 会话ID
- **响应体**:
  ```json
  {
    "code": 200,
    "message": "删除成功",
    "data": null
  }
  ```

### 3.5 更新会话记忆
- **接口路径**: `PUT /api/conversation/{conversation_id}/memory`
- **功能**: 更新会话的短期记忆数据
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `conversation_id`: 会话ID
- **请求体**:
  ```json
  {
    // 记忆数据对象
    "current_topic": "唐诗宋词",
    "game_state": "playing"
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": null
  }
  ```

## 4. 消息接口 (Message API)

### 4.1 获取单条消息详情
- **接口路径**: `GET /api/message/{message_id}`
- **功能**: 获取单条消息的详细信息
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `message_id`: 消息ID
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "id": 456,
      "role": "user",            // user, assistant, system
      "content": "消息内容",
      "created_at": "2024-01-01T00:00:00"
    }
  }
  ```

## 5. 诗词接口 (Poetry API)

### 5.1 搜索诗词
- **接口路径**: `POST /api/poetry/search`
- **功能**: 搜索诗词内容
- **请求体**:
  ```json
  {
    "query": "春风",             // 搜索查询词
    "search_type": "hybrid",     // 搜索类型: keyword, vector, hybrid
    "top_k": 5                   // 返回结果数量，默认5
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "total": 3,
      "items": [
        {
          "id": 789,
          "title": "春晓",
          "dynasty": "唐代",
          "writer": "孟浩然",
          "content": "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
          "score": 0.95              // 相似度分数(向量搜索时)
        }
      ]
    }
  }
  ```

## 错误响应格式

所有接口在出错时都会返回统一的错误格式：

```json
{
  "code": 400,
  "message": "错误描述信息",
  "data": null
}
```

常见HTTP状态码：
- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 未授权/Token无效
- `404`: 资源不存在
- `500`: 服务器内部错误

## 认证说明

除认证接口外，所有接口都需要在请求头中携带JWT Token：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Token有效期为24小时，过期后需要重新登录获取新的Token。

## 数据类型说明

- `datetime`: ISO 8601格式的时间字符串，如 `"2024-01-01T00:00:00"`
- `RoleType`: 枚举类型，可选值为 `"user"`, `"assistant"`, `"system"`
- `search_type`: 枚举类型，可选值为 `"keyword"`, `"vector"`, `"hybrid"`