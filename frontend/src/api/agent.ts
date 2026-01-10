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
export function runAgent(agentId: number, data: { user_input: string; conversation_id: number; workflow?: string; history_limit?: number }) {
    return request.post(prefix + `/${agentId}/run`, data);
}
// }

