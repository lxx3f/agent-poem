from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError

from app.core.config import settings
from app.core.exceptions import BusinessException
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.user_service import UserService
from app.schemas.user import UserItem

security = HTTPBearer(auto_error=False)


def create_access_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    '''
    创建访问令牌
    
    :param user_id: 用户 ID
    :type user_id: int
    :param expires_delta: 过期时间
    :type expires_delta: Optional[timedelta]
    :return: 访问令牌
    :rtype: str
    '''
    expire = datetime.now() + (expires_delta or timedelta(
        minutes=settings.jwt_access_token_expire_minutes))

    payload = {
        "user_id": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def parse_access_token(token: str) -> int:
    '''
    解析访问令牌
    
    :param token: 访问令牌
    :type token: str
    :return: 用户 ID
    :rtype: int
    '''
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        sub = payload.get("user_id")
        if sub is None:
            raise BusinessException(
                code=401,
                message="Invalid or expired token",
            )
        user_id = int(sub)
        return user_id
    except (JWTError, ValueError):
        raise BusinessException(
            code=401,
            message="Invalid or expired token",
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(
    security)) -> Dict[str, Any]:
    '''
    获取当前用户
    
    :param credentials: 认证信息
    :type credentials: HTTPAuthorizationCredentials
    :return: 用户信息
    :rtype: Dict[str, Any]
    '''
    if credentials is None:
        raise BusinessException(code=401, message="未登录")

    token = credentials.credentials
    try:
        payload = jwt.decode(token,
                             settings.jwt_secret_key,
                             algorithms=[settings.jwt_algorithm])
        user_id: int | None = payload.get("user_id")
        if user_id is None:
            raise BusinessException(code=401, message="Token 中缺少 user_id")
        user_service = UserService()
        user = user_service.get_user_by_id(user_id)
        return user

    except JWTError:
        raise BusinessException(code=401, message="Token 无效或已过期")
