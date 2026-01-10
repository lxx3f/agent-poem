// 用户认证相关接口
import request from '../utils/request';

// 注册
export function register(data: { email: string; password: string; nickname?: string }) {
  return request.post('/api/auth/register', data);
}

// 登录
export function login(data: { email: string; password: string }) {
  return request.post('/api/auth/login', data);
}

// 获取当前用户信息
export function getMe() {
  return request.get('/api/auth/me');
}

// 更新用户信息
export function updateProfile(data: { nickname: string }) {
  return request.post('/api/auth/update', data);
}
