from datetime import datetime, timezone
from typing import Optional, Dict, Any

import pymysql
import hashlib
from passlib.context import CryptContext

from backend.app.core.config import settings
from backend.app.core.exceptions import BusinessException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    def __init__(self):
        self.conn = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            charset=settings.db_charset,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    # ---------- 密码相关 ----------

    def _hash_password(self, password: str) -> str:
        print(f"psw: {password}")
        password_bytes = password.encode("utf-8")
        sha256 = hashlib.sha256(password_bytes).hexdigest()
        print(f"sha256: {sha256}")
        return pwd_context.hash(sha256)

    def _verify_password(self, password: str, hashed: str) -> bool:
        password_bytes = password.encode("utf-8")
        sha256 = hashlib.sha256(password_bytes).hexdigest()
        return pwd_context.verify(sha256, hashed)

    # ---------- 核心业务 ----------

    def create_user(self, email: str, nickname: str,
                    password: str) -> Dict[str, Any]:
        with self.conn.cursor() as cursor:
            # 1. 邮箱唯一性校验
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email, ),
            )
            if cursor.fetchone():
                raise BusinessException(403, "邮箱已注册")

            # 2. 插入用户
            password_hash = self._hash_password(password)
            now = datetime.now(timezone.utc)

            cursor.execute(
                """
                INSERT INTO users (email, password_hash, username, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (email, password_hash, nickname, now),
            )

            user_id = cursor.lastrowid

            return {
                "id": user_id,
                "email": email,
                "nickname": nickname,
                "created_at": now,
            }

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, password_hash
                FROM users
                WHERE email = %s
                """,
                (email, ),
            )
            user = cursor.fetchone()

            if not user:
                raise BusinessException(404,
                                        "authenticate error: email not found")

            if not self._verify_password(password, user["password_hash"]):
                raise BusinessException(
                    403, "authenticate error: password or email error")

            return {
                "id": user["id"],
                "email": user["email"],
            }

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, username, created_at
                FROM users
                WHERE id = %s
                """,
                (user_id, ),
            )
            row = cursor.fetchone()
            if row is None:
                raise BusinessException(404, "user not found")
            return row

    def exists(self, user_id: int) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM users WHERE id = %s",
                (user_id, ),
            )
            return cursor.fetchone() is not None
