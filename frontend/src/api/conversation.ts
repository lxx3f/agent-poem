// 会话相关接口
import request from '../utils/request';

const prefix = '/conversation';

// 创建新会话
export function createConversation(data: { title?: string; agent_id: number }) {
    return request.post(prefix + '/create', data);
}

// 删除会话
export function deleteConversation(conversationId: number) {
    return request.delete(prefix + `/${conversationId}`);
}

// 获取会话消息列表
export function listMessagesByConversation(conversationId: number, data: { conversation_id: number; limit?: number }) {
    return request.post(`${prefix}/${conversationId}/messages`, data);
}

// 获取会话列表
export function listConversations(data: { agent_id: number; limit?: number; offset?: number }) {
    return request.post(prefix + '/list', data);
}