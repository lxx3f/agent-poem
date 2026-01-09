from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.schemas.user import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserUpdateRequest,
    UserLoginRequest,
)
from backend.app.core.jwt import create_access_token, get_current_user
from backend.app.core.response import success_response
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["Auth"])

user_service = UserService()


@router.post("/register")
def register_user(req: UserRegisterRequest):
    '''
    注册用户
    
    :param req: 请求体
    :type req: UserRegisterRequest
    '''
    user = user_service.create_user(
        email=req.email,
        password=req.password,
        nickname=req.nickname,
    )

    return success_response(data={
        "id": user["id"],
        "email": user["email"],
        "nickname": user["nickname"]
    })


@router.post("/login")
def login(req: UserLoginRequest):
    '''
    用户登录
    
    :param req: 登录请求体
    :type req: UserLoginRequest
    '''
    user = user_service.authenticate(
        email=req.email,
        password=req.password,
    )

    token = create_access_token(user["id"])
    return success_response({
        "access_token": token,
        "token_type": "Bearer",
    })


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    '''
    获取当前用户信息
    '''
    return success_response(
        data={
            "id": current_user["id"],
            "email": current_user["email"],
            "nickname": current_user["nickname"]
        })


@router.post("/update")
def update_profile(req: UserUpdateRequest,
                   current_user=Depends(get_current_user)):
    '''
    更新用户信息
    
    :param req: 请求体
    :type req: UserUpdateRequest
    '''
    user_service.update_user(current_user["id"], req.nickname)

    return success_response(message="更新成功")
