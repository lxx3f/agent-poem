from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.schemas.user import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
)
from backend.app.core.jwt import create_access_token, get_current_user
from backend.app.core.response import success_response
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["Auth"])

user_service = UserService()


@router.post("/register")
def register_user(req: UserRegisterRequest):

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
    return success_response(
        data={
            "id": current_user["id"],
            "email": current_user["email"],
            "nickname": current_user["nickname"]
        })


@router.post("/update")
def update_profile(req: UserRegisterRequest,
                   current_user=Depends(get_current_user)):
    # TODO 更新用户资料API

    return success_response(message="TODO", data={})
