// 消息相关接口
import request from '../utils/request';

// 获取单条消息详情
export function getMessage(messageId: number) {
  return request.get(`/api/message/${messageId}`);
}
