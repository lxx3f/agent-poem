// 本地存储工具
export function setItem(key: string, value: any) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function getItem(key: string) {
  const value = localStorage.getItem(key);
  return value ? JSON.parse(value) : null;
}

export function removeItem(key: string) {
  localStorage.removeItem(key);
}
