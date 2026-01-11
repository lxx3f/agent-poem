'''
提供基础的 MySQL 数据库操作服务
'''
import pymysql
from typing import List, Any, Dict, Optional, cast
from datetime import datetime, timezone
from app.core.exceptions import BusinessException
from app.core.config import settings


class MySQLService:

    def __init__(self):
        self.conn = self.get_conn()

    def get_conn(self) -> pymysql.Connection:
        '''
        获取数据库连接,返回 Connection 对象
        
        :param self: 说明
        :return: 说明
        :rtype: Connection
        '''
        return pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            charset=settings.db_charset,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    # =====================
    # Poetry
    # =====================
    def search_poetry_ids_by_keyword(
        self,
        keyword: str,
        limit: int,
    ) -> List[int]:
        '''
        根据关键词搜索诗词，返回 poetry_id 列表，顺序不限, 最多返回 limit 条
        
        :param self: 说明
        :param keyword: 说明
        :type keyword: str
        :param limit: 说明
        :type limit: int
        :return: 说明
        :rtype: List[int]
        '''
        sql = """
        SELECT id
        FROM poetry
        WHERE content LIKE %s
           OR title LIKE %s
        LIMIT %s
        """
        like = f"%{keyword}%"

        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (like, like, limit))
            rows = cursor.fetchall()
        return [row["id"] for row in rows]

    def get_poetry_by_ids(
        self,
        ids: List[int],
    ) -> List[Dict[str, Any]]:
        '''
        根据 poetry_id 列表获取诗词列表, 顺序不限, 要求 ids 非空
        
        :param self: 说明
        :param ids: 说明
        :type ids: List[int]
        :return: 说明
        :rtype: List[Dict[str, Any]]
        '''
        sql = f"""
        SELECT
            p.id,
            p.title,
            p.content,
            p.dynasty,
            w.name
        FROM poetry p
        LEFT JOIN writer w ON p.writer_id = w.id
        WHERE p.id IN ({",".join(["%s"] * len(ids))})
    """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, tuple(ids))
            rows = cursor.fetchall()
        return list(rows)

    # =====================
    # User
    # =====================
    def user_exists(self, user_id: int) -> bool:
        """
        检查用户是否存在
        
        :param self: 说明
        :param user_id: 说明
        :type user_id: int
        :return: 说明
        :rtype: bool
        """
        sql = "SELECT 1 FROM users WHERE id = %s LIMIT 1"
        cursor = self.conn.cursor()
        cursor.execute(sql, (user_id, ))
        return cursor.fetchone() is not None

    def email_exists(self, email: str) -> bool:
        '''
        检查邮箱是否已存在
        
        :param self: 说明
        :param email: 说明
        :type email: str
        :return: 说明
        :rtype: bool
        '''
        sql = "SELECT 1 FROM users WHERE email = %s LIMIT 1"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (email, ))
            return cursor.fetchone() is not None

    def create_user(self, email: str, nickname: str,
                    password_hash: str) -> Dict[str, Any]:
        '''
        插入新用户，返回用户信息，要求 email 不存在
        
        :param self: 说明
        :param email: 说明
        :type email: str
        :param nickname: 说明
        :type nickname: str
        :param password: 说明
        :type password: str
        :return: 说明
        :rtype: Dict[str, Any]
        '''
        sql = """
            INSERT INTO users (email, password_hash, username, created_at)
            VALUES (%s, %s, %s, %s)
            """
        with self.conn.cursor() as cursor:
            now = datetime.now(timezone.utc)
            cursor.execute(
                sql,
                (email, password_hash, nickname, now),
            )
            user_id = cursor.lastrowid
            return {
                "id": user_id,
                "email": email,
                "nickname": nickname,
                "created_at": now,
            }

    def delete_user(self, user_id: int) -> None:
        '''
        删除用户，要求 user_id 存在
        
        :param self: 说明
        :param user_id: 说明
        :type user_id: int
        :return: 说明
        :rtype: None
        '''
        sql = "DELETE FROM users WHERE id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (user_id, ))

    def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        nickname: Optional[str] = None,
        password_hash: Optional[str] = None,
    ) -> None:
        '''
        更新用户信息, 只更新提供的字段，要求 user_id 存在
        
        :param self: 说明
        :param user_id: 说明
        :type user_id: int
        :param email: 说明
        :type email: str
        :param nickname: 说明
        :type nickname: str
        :param password_hash: 说明
        :type password_hash: str
        :return: 说明
        :rtype: None
        '''
        if not any([email, nickname, password_hash]):
            return
        fields = []
        params = []
        if email is not None:
            fields.append("email = %s")
            params.append(email)
        if nickname is not None:
            fields.append("username = %s")
            params.append(nickname)
        if password_hash is not None:
            fields.append("password_hash = %s")
            params.append(password_hash)
        params.append(user_id)
        sql = f"""
        UPDATE users
        SET {', '.join(fields)}
        WHERE id = %s
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, tuple(params))

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        '''
        根据 user_id 获取用户信息, 要求 user_id 存在
        
        :param self: 说明
        :param user_id: 说明
        :type user_id: int
        :return: 说明
        :rtype: Dict[str, Any]
        '''
        sql = """
                SELECT id, email, username, created_at, updated_at
                FROM users
                WHERE id = %s
                """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                sql,
                (user_id, ),
            )
            row = cursor.fetchone()
            if row is None:
                raise BusinessException(404, "mysql error: user not found")
            return {
                "id": row["id"],
                "email": row["email"],
                "nickname": row["username"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        '''
        根据 email 获取用户信息, 要求email存在且唯一
        
        :param self: 说明
        :param email: 说明
        :type email: str
        :return: 说明
        :rtype: Optional[Dict[str, Any]]
        '''
        sql = """
                SELECT id, email, username, password_hash, created_at, updated_at
                FROM users
                WHERE email = %s
                """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                sql,
                (email, ),
            )
            row = cursor.fetchone()
            if row is None:
                raise BusinessException(404, "mysql error: user not found")
            return {
                "id": row["id"],
                "email": row["email"],
                "nickname": row["username"],
                "password_hash": row["password_hash"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    # =====================
    # Agent
    # =====================
    def get_agents(self, limit: int) -> List[Dict[str, Any]]:
        '''
        获取 agent 列表, 最多返回 limit 条
        
        :param self: 说明
        :param limit: 说明
        :type limit: int
        :return: 说明
        :rtype: List[Dict[str, Any]]
        '''
        sql = """
                SELECT id, name, code, description, workflow_key, system_prompt, parameters, llm_config, is_active, created_at, updated_at
                FROM agents
                LIMIT %s
                """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (limit, ))
            return list(cursor.fetchall())

    def get_agent_by_id(self, agent_id: int) -> Dict[str, Any]:
        '''
        根据 ID 获取 Agent 详情, 要求 agent_id 存在
        
        :param self: 说明
        :param agent_id: 说明
        :type agent_id: int
        :return: 说明
        :rtype: Dict[str, Any]
        '''
        sql = """
                SELECT id, name, code, description, workflow_key, system_prompt, parameters, llm_config, is_active, created_at, updated_at
                FROM agents
                WHERE id = %s
                """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (agent_id, ))
            row = cursor.fetchone()
            if row is None:
                raise BusinessException(404, "mysql error: agent not found")
            return row

    # =====================
    # Conversation
    # =====================
    def check_conversation_exists(
        self,
        conversation_id: int,
    ) -> bool:
        '''
        检查会话是否存在
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :return: 说明
        :rtype: bool
        '''
        sql = "SELECT 1 FROM conversations WHERE id = %s LIMIT 1"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (conversation_id, ))
            return cursor.fetchone() is not None

    def create_conversation(
        self,
        user_id: int,
        agent_id: int,
        title: str,
    ) -> int:
        '''
        创建新会话，返回 conversation_id
        '''
        sql = """
        INSERT INTO conversations (user_id, title, agent_id, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        now = datetime.now(timezone.utc)
        cursor.execute(sql, (user_id, title, agent_id, now, now))
        return cursor.lastrowid

    def delete_conversation(
        self,
        conversation_id: int,
    ) -> None:
        '''
        删除会话，要求 conversation_id 存在
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :return: 说明
        :rtype: None
        '''
        sql = "DELETE FROM conversations WHERE id = %s"
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (conversation_id, ))

    def get_conversations_by_user_agent(
        self,
        user_id: int,
        agent_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        '''
        获取用户对应agent的会话列表, 顺序按 updated_at 降序排列, 要求user_id存在
        
        :param self: 
        :param user_id: 
        :type user_id: int
        :param agent_id: 
        :type agent_id: int
        :param limit: 
        :type limit: int
        :param offset: 
        :type offset: int
        :return: 
        :rtype: List[Dict[str, Any]]
        '''
        sql = """
        SELECT id, title, agent_id, created_at, updated_at
        FROM conversations
        WHERE user_id = %s AND agent_id = %s
        ORDER BY updated_at DESC
        LIMIT %s OFFSET %s
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (user_id, agent_id, limit, offset))
        rows = cursor.fetchall()
        return list(rows)

    def conversation_belongs_to_user(
        self,
        conversation_id: int,
        user_id: int,
    ) -> bool:
        '''
        检查会话是否属于该用户
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :param user_id: 说明
        :type user_id: int
        :return: 说明
        :rtype: bool
        '''
        sql = """
        SELECT 1
        FROM conversations
        WHERE id = %s AND user_id = %s
        LIMIT 1
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (conversation_id, user_id))
        return cursor.fetchone() is not None

    def get_conversation_by_id(
        self,
        conversation_id: int,
    ) -> Dict[str, Any]:
        '''
        根据 conversation_id 获取会话详情，要求 conversation_id 存在
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :return: 说明
        :rtype: Dict[str, Any]
        '''
        sql = """
        SELECT id, user_id, title, agent_id, created_at, updated_at
        FROM conversations
        WHERE id = %s
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (conversation_id, ))
        row = cursor.fetchone()
        if row is None:
            raise BusinessException(404, "mysql error: conversation not found")
        return row

    # =====================
    # Message
    # =====================
    def message_exists(
        self,
        message_id: int,
    ) -> bool:
        '''
        检查消息是否存在
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :return: 说明
        :rtype: bool
        '''
        sql = "SELECT 1 FROM messages WHERE id = %s LIMIT 1"
        cursor = self.conn.cursor()
        cursor.execute(sql, (message_id, ))
        return cursor.fetchone() is not None

    def create_message(
        self,
        conversation_id: int,
        role: str,
        status: str,
        content: str,
    ) -> int:
        '''
        添加消息到会话，返回 message_id，要求 conversation_id 存在
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :param user_id: 说明
        :type user_id: int
        :param role: ENUM('user', 'assistant', 'system')
        :type role: str
        :param status: ENUM('pending', 'done', 'failed')
        :type status: str
        :param content: 说明
        :type content: str
        :return: 说明
        :rtype: int
        '''
        sql = """
        INSERT INTO messages (conversation_id, role, status, content, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        now = datetime.now(timezone.utc)
        cursor.execute(
            sql,
            (conversation_id, role, status, content, now),
        )
        return cursor.lastrowid

    def delete_message(
        self,
        message_id: int,
    ) -> None:
        '''
        删除消息，要求 message_id 存在
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :return: 说明
        :rtype: None
        '''
        sql = "DELETE FROM messages WHERE id = %s"
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (message_id, ))

    def update_message_status(
        self,
        message_id: int,
        status: str,
    ) -> None:
        '''
        更新消息状态，要求 message_id 存在
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :param status: ENUM('pending', 'done', 'failed')
        :type status: str
        :return: 说明
        :rtype: None
        '''
        sql = """
        UPDATE messages
        SET status = %s
        WHERE id = %s
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (status, message_id))

    def update_message_content(
        self,
        message_id: int,
        content: str,
    ) -> None:
        '''
        更新消息内容，要求 message_id 存在
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :param content: 说明
        :type content: str
        :return: 说明
        :rtype: None
        '''
        sql = """
        UPDATE messages
        SET content = %s
        WHERE id = %s
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (content, message_id))

    def get_messages_by_conversation(
        self,
        conversation_id: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        '''
        获取会话的消息列表，按 created_at 正序排列，要求 conversation_id 存在
        
        :param self: 说明
        :param conversation_id: 说明
        :type conversation_id: int
        :param limit: 说明
        :type limit: int
        :return: 说明
        :rtype: List[Dict[str, Any]]
        '''
        sql = """
        SELECT id, role, status, content, created_at
        FROM messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
        LIMIT %s
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (conversation_id, limit))
        rows = cursor.fetchall()
        return list(rows)

    def get_message_by_id(
        self,
        message_id: int,
    ) -> Dict[str, Any]:
        '''
        根据 message_id 获取消息，要求 message_id 存在
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :return: 说明
        :rtype: Dict[str, Any]
        '''
        sql = """
        SELECT id, conversation_id, role, status, content, created_at
        FROM messages
        WHERE id = %s
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (message_id, ))
        row = cursor.fetchone()
        if row is None:
            raise BusinessException(404, "mysql error: message not found")
        return row

    def message_belongs_to_user(
        self,
        message_id: int,
        user_id: int,
    ) -> bool:
        '''
        检查消息是否属于该用户
        
        :param self: 说明
        :param message_id: 说明
        :type message_id: int
        :param user_id: 说明
        :type user_id: int
        :return: 说明
        :rtype: bool
        '''
        sql = """
        SELECT 1
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE m.id = %s AND c.user_id = %s
        LIMIT 1
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (message_id, user_id))
        return cursor.fetchone() is not None
