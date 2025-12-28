from typing import List, Dict, Any, Optional, Literal

import pymysql

from backend.app.core.exceptions import BusinessException
from backend.app.services.mysql_service import MySQLService
from backend.app.schemas.conversation import (
    ConversationItem,
    MessageItem,
)

RoleType = Literal["user", "assistant", "system"]


class ConversationService:

    def __init__(self, mysql_service: MySQLService = MySQLService()):
        self.mysql = mysql_service

    def _check_user_exists(self, user_id: int):
        if not self.mysql.user_exists(user_id):
            raise BusinessException(
                code=404,
                message="User does not exist",
            )

    def _check_conversation_owner(
        self,
        conversation_id: int,
        user_id: int,
    ):
        if not self.mysql.conversation_belongs_to_user(
                conversation_id,
                user_id,
        ):
            raise BusinessException(
                code=403,
                message="Conversation not found or access denied",
            )

    # =====================
    # Conversation
    # =====================

    def create_conversation(
        self,
        user_id: int,
        title: str,
    ) -> int:
        """
        创建新会话，返回 conversation_id
        """

        self._check_user_exists(user_id)

        sql = """
        INSERT INTO conversations (user_id, title)
        VALUES (%s, %s)
        """
        cursor = self.mysql.get_conn().cursor()
        cursor.execute(sql, (user_id, title))
        cursor.connection.commit()
        return cursor.lastrowid

    def get_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        获取会话并校验归属
        """
        self._check_user_exists(user_id)
        sql = """
        SELECT id, user_id, title, created_at, updated_at
        FROM conversations
        WHERE id = %s
        """
        cursor = self.mysql.get_conn().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (conversation_id, ))
        row = cursor.fetchone()

        if not row:
            raise BusinessException(404, "会话不存在")

        if row["user_id"] != user_id:
            raise BusinessException(403, "无权访问该会话")

        return row

    def list_conversations(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出用户的会话列表
        """

        self._check_user_exists(user_id)

        sql = """
        SELECT id, title, created_at, updated_at
        FROM conversations
        WHERE user_id = %s
        ORDER BY updated_at DESC
        LIMIT %s OFFSET %s
        """
        cursor = self.mysql.get_conn().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (user_id, limit, offset))
        rows = cursor.fetchall()
        return list(rows)

    # =====================
    # Message
    # =====================

    def add_message(
        self,
        conversation_id: int,
        user_id: int,
        role: RoleType,
        content: str,
    ) -> int:
        """
        向会话中追加一条消息
        """
        # 校验会话归属
        self.get_conversation(conversation_id, user_id)

        sql = """
        INSERT INTO messages (conversation_id, role, content)
        VALUES (%s, %s, %s)
        """
        cursor = self.mysql.get_conn().cursor()
        cursor.execute(sql, (conversation_id, role, content))
        cursor.connection.commit()
        return cursor.lastrowid

    def list_messages(
        self,
        conversation_id: int,
        user_id: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取会话消息（按时间正序）
        """
        # 校验会话归属
        self.get_conversation(conversation_id, user_id)

        sql = """
        SELECT id, role, content, created_at
        FROM messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
        LIMIT %s
        """
        cursor = self.mysql.get_conn().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (conversation_id, limit))
        rows = cursor.fetchall()
        return list(rows)
