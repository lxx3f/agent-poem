// 智能体相关接口
import request from '../utils/request';

export function fetchAgents() {
  return request.get('/api/agent/list');
}
