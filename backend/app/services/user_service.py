from datetime import datetime, timezone
from typing import Optional, Dict, Any
import hashlib
from passlib.context import CryptContext

from app.core.config import settings
from app.services.mysql_service import MySQLService
from app.core.exceptions import BusinessException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    用户管理服务
    """

    def __init__(self):
        pass

    # ---------- 密码相关 ----------

    def _hash_password(self, password: str) -> str:
        # print(f"psw: {password}")
        password_bytes = password.encode("utf-8")
        sha256 = hashlib.sha256(password_bytes).hexdigest()
        # print(f"sha256: {sha256}")
        return pwd_context.hash(sha256)

    def _verify_password(self, password: str, hashed: str) -> bool:
        password_bytes = password.encode("utf-8")
        sha256 = hashlib.sha256(password_bytes).hexdigest()
        return pwd_context.verify(sha256, hashed)

    # ---------- 核心业务 ----------

    def create_user(self, email: str, nickname: str,
                    password: str) -> Dict[str, Any]:
        '''
        创建新用户，返回用户信息
        
        :param email: 用户邮箱
        :type email: str
        :param nickname: 用户昵称
        :type nickname: str
        :param password: 用户密码
        :type password: str
        :return: 用户信息
        :rtype: Dict[str, Any]
        '''
        mysql_service = MySQLService()
        # 1. 邮箱唯一性校验
        if mysql_service.email_exists(email):
            raise BusinessException(
                400, "create user failed: email already registered")
        # 2. 插入用户
        password_hash = self._hash_password(password)
        return mysql_service.create_user(
            email=email,
            nickname=nickname,
            password_hash=password_hash,
        )

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        '''
        认证用户，成功则返回用户信息, 失败则抛出异常
        
        :param email: 用户邮箱
        :type email: str
        :param password: 用户密码
        :type password: str
        :return: 用户信息
        :rtype: Dict[str, Any]
        '''
        mysql_service = MySQLService()
        if mysql_service.email_exists(email) is False:
            raise BusinessException(404,
                                    "authenticate failed: email not found")
        user = mysql_service.get_user_by_email(email=email)
        if not self._verify_password(password, user["password_hash"]):
            raise BusinessException(401,
                                    "authenticate failed: invalid password")
        return user

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        '''
        根据 user_id 获取用户信息
        
        :param user_id: 用户 id
        :type user_id: int
        :return: 用户信息
        :rtype: Dict[str, Any]
        '''
        mysql_service = MySQLService()
        return mysql_service.get_user_by_id(user_id=user_id)

    def update_user(self, user_id: int, nickname: str) -> None:
        '''
        更新用户信息

        :param user_id: 用户 id
        :type user_id: int
        :param nickname: 用户昵称
        :type nickname: str
        :return: 用户信息
        :rtype: Dict[str, Any]
        '''
        mysql_service = MySQLService()
        return mysql_service.update_user(user_id=user_id, nickname=nickname)
