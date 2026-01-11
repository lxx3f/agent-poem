from fastapi import APIRouter, Depends

from app.schemas.user import (UserRegisterRequest, UserRegisterResponse,
                              UserUpdateRequest, UserLoginRequest, UserItem,
                              UserLoginResponse)
from app.core.jwt import create_access_token, get_current_user
from app.core.response import success_response, StandardResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register",
             response_model=StandardResponse[UserRegisterResponse])
def register_user(req: UserRegisterRequest):
    '''
    注册用户
    
    :param req: 请求体
    :type req: UserRegisterRequest
    '''
    user_service = UserService()
    user = user_service.create_user(
        email=req.email,
        password=req.password,
        nickname=req.nickname,
    )
    response = UserRegisterResponse(id=user["id"],
                                    email=user["email"],
                                    nickname=user["nickname"])

    return success_response(message="注册成功", data=response)


@router.post("/login", response_model=StandardResponse[UserLoginResponse])
def login(req: UserLoginRequest):
    '''
    用户登录
    
    :param req: 登录请求体
    :type req: UserLoginRequest
    '''
    user_service = UserService()
    user = user_service.authenticate(
        email=req.email,
        password=req.password,
    )

    token = create_access_token(user["id"])
    response = UserLoginResponse(access_token=token, token_type="Bearer")
    return success_response(message="登录成功", data=response)


@router.get("/me", response_model=StandardResponse[UserItem])
def get_me(current_user=Depends(get_current_user)):
    '''
    获取当前用户信息
    '''
    response = UserItem(
        id=current_user["id"],
        email=current_user["email"],
        nickname=current_user["nickname"],
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"],
    )
    return success_response(data=response)


@router.post("/update", response_model=StandardResponse[None])
def update_profile(req: UserUpdateRequest,
                   current_user=Depends(get_current_user)):
    '''
    更新用户信息
    
    :param req: 请求体
    :type req: UserUpdateRequest
    '''
    user_service = UserService()
    user_service.update_user(current_user["id"], req.nickname)
    return success_response(message="更新成功")
