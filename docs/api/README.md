# API接口文档

## 文档目录

- [API接口文档](./API接口文档.md) - 完整的API接口说明文档

## 接口概览

本项目提供以下五大模块的API接口：

### 1. 认证接口 (Auth API)
- 用户注册 `/api/auth/register`
- 用户登录 `/api/auth/login`  
- 获取用户信息 `/api/auth/me`
- 更新用户信息 `/api/auth/update`

### 2. 智能体接口 (Agent API)
- 列出智能体 `/api/agent/list`
- 获取智能体详情 `/api/agent/{agent_id}`
- 运行智能体 `/api/agent/{agent_id}/run`
- 更新系统提示词 `/api/agent/{agent_id}/update_system_prompt`

### 3. 会话接口 (Conversation API)
- 创建会话 `/api/conversation/create`
- 列出会话消息 `/api/conversation/{conversation_id}/messages`
- 列出用户会话 `/api/conversation/list`
- 删除会话 `/api/conversation/{conversation_id}`
- 更新会话记忆 `/api/conversation/{conversation_id}/memory`

### 4. 消息接口 (Message API)
- 获取消息详情 `/api/message/{message_id}`

### 5. 诗词接口 (Poetry API)
- 搜索诗词 `/api/poetry/search`

## 认证方式

除认证接口外，所有接口都需要在请求头中携带JWT Token：

```
Authorization: Bearer <your_token_here>
```

## 响应格式

所有接口都采用统一的响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

## 错误处理

接口出错时会返回相应的HTTP状态码和错误信息：

- 400: 请求参数错误
- 401: 未授权/Token无效  
- 404: 资源不存在
- 500: 服务器内部错误

详细的接口说明请参考 [API接口文档](./API接口文档.md)。