from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=6, description="用户密码")
    nickname: str = Field("默认昵称", description="用户昵称")


class UserRegisterResponse(BaseModel):
    id: int


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")


class UserItem(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    created_at: datetime
    updated_at: datetime


class UserUpdateRequest(BaseModel):
    nickname: str = Field("默认昵称", description="昵称")
