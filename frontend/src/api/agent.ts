// 智能体相关接口
import request from '../utils/request';


const prefix = '/agent';

// 获取智能体列表
export function listAgents(data: { limit?: number }) {
    return request.post(prefix + '/list', data);
}

// 获取智能体详情
export function getAgent(agentId: number) {
    return request.get(prefix + `/${agentId}`);
}

// 运行智能体
export function runAgent(agentId: number, data: { user_input: string; conversation_id: number; history_limit?: number }) {
    return request.post(prefix + `/${agentId}/run`, data);
}

// 更新智能体的system_prompt
export function updateAgentSystemPrompt(agentId: number, data: { system_prompt: string }) {
    return request.post(prefix + `/${agentId}/update_system_prompt`, data);
}

