// 聊天相关接口
import request from '../utils/request';

export function sendMessage(data: any) {
  return request.post('/api/chat/send', data);
}
