// 消息相关接口
import request from '../utils/request';

const prefix = '/message';
// 获取单条消息详情
export function getMessage(messageId: number) {
  return request.get(prefix + `/${messageId}`);
}
