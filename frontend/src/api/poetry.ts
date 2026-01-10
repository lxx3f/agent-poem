import request from '../utils/request';

// 搜索诗词
export function searchPoetry(data: {
  query: string;
  search_type?: 'keyword' | 'vector' | 'hybrid';
  top_k?: number;
}) {
  return request.post('/api/poetry/search', data);
}
