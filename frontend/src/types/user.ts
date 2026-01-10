export interface UserRegisterRequest {
  email: string;
  password: string;
  nickname?: string;
}

export interface UserRegisterResponse {
  id: number;
  email: string;
  nickname: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserLoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserItem {
  id: number;
  email: string;
  nickname: string;
  created_at: string;
  updated_at: string;
}

export interface UserUpdateRequest {
  nickname: string;
}
