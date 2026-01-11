# API设计文档

# 统一响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": [...]
}
```
字段说明:

|字段名 |	类型 | 说明 |
| ---- | ---  | ---- |
| code | integer	|状态码，200 表示成功 |
| message	| string	| 状态说明 |
|data |	json |	业务数据 |

---
设计原则：
service层写处理逻辑，返回dict，api层封装

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
      "id": "number",
      "email": "string",
      "nickname": "string"
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
      "access_token": "string",
      "token_type": "string"
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
      "id": "number",
      "email": "string",
      "nickname": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
  ```

### 1.4 更新用户信息
- **接口路径**: `POST /api/auth/update`
- **功能**: 更新用户信息
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

## 2. 诗词接口 (Poetry API)

### 2.1 搜索诗词
- **接口路径**: `POST /api/poetry/search`
- **功能**: 搜索诗词
- **请求体**:
  ```json
  {
    "query": "string",           // 搜索查询词
    "search_type": "string",     // 搜索类型: semantic, keyword, random
    "top_k": "number"            // 返回结果数量，默认5
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "total": "number",
      "items": [
        {
          "id": "number",
          "title": "string",
          "dynasty": "string",
          "writer": "string",
          "content": "string",
          "score": "number"
        }
      ]
    }
  }
  ```

## 3. 智能体接口 (Agent API)

### 3.1 列出所有智能体
- **接口路径**: `POST /api/agent/list`
- **功能**: 获取所有可用的智能体列表
- **认证**: 需要在Header中携带JWT Token
- **请求体**:
  ```json
  {
    "limit": "number"            // 限制返回数量，默认20
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "total": "number",
      "agents": [
        {
          "id": "number",
          "name": "string",
          "code": "string",
          "description": "string",
          "workflow_key": "string",
          "system_prompt": "string",
          "parameters": "json",
          "llm_config": "json",
          "is_active": "number",
          "created_at": "datetime",
          "updated_at": "datetime"
        }
      ]
    }
  }
  ```

### 3.2 获取智能体详情
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
      "id": "number",
      "name": "string",
      "code": "string",
      "description": "string",
      "workflow_key": "string",
      "system_prompt": "string",
      "parameters": "json",
      "llm_config": "json",
      "is_active": "number",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
  ```

### 3.3 运行智能体
- **接口路径**: `POST /api/agent/{agent_id}/run`
- **功能**: 运行特定智能体
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `agent_id`: 智能体ID
- **请求体**:
  ```json
  {
    "user_input": "string",      // 用户输入
    "conversation_id": "number", // 会话ID，可选
    "workflow": "string"         // 工作流，可选
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "message": "string"         // 智能体回复
    }
  }
  ```

## 4. 会话接口 (Conversation API)

### 4.1 创建会话
- **接口路径**: `POST /api/conversation/create`
- **功能**: 创建新会话
- **认证**: 需要在Header中携带JWT Token
- **请求体**:
  ```json
  {
    "agent_id": "number",        // 智能体ID
    "title": "string"            // 会话标题，可选
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "conversation_id": "number"
    }
  }
  ```

### 4.2 列出会话消息
- **接口路径**: `POST /api/conversation/{conversation_id}/messages`
- **功能**: 获取指定会话的消息列表
- **认证**: 需要在Header中携带JWT Token
- **路径参数**:
  - `conversation_id`: 会话ID
- **请求体**:
  ```json
  {
    "limit": "number"            // 限制返回数量，默认50
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "conversation_id": "number",
      "total": "number",
      "messages": [
        {
          "id": "number",
          "conversation_id": "number",
          "role": "string",        // user, assistant, system
          "content": "string",
          "status": "string",      // pending, done, failed
          "created_at": "datetime"
        }
      ]
    }
  }
  ```

### 4.3 列出用户会话
- **接口路径**: `POST /api/conversation/list`
- **功能**: 获取用户的会话列表
- **认证**: 需要在Header中携带JWT Token
- **请求体**:
  ```json
  {
    "agent_id": "number",        // 智能体ID，可选
    "limit": "number",           // 限制返回数量，默认20
    "offset": "number"           // 偏移量，默认0
  }
  ```
- **响应体**:
  ```json
  {
    "code": 200,
    "data": {
      "total": "number",
      "conversations": [
        {
          "id": "number",
          "user_id": "number",
          "title": "string",
          "agent_id": "number",
          "created_at": "datetime",
          "updated_at": "datetime"
        }
      ]
    }
  }
  ```

### 4.4 删除会话
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

## 5. 消息接口 (Message API)

### 5.1 获取单条消息详情
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
      "id": "number",
      "conversation_id": "number",
      "role": "string",          // user, assistant, system
      "content": "string",
      "status": "string",        // pending, done, failed
      "created_at": "datetime"
    }
  }
  ```