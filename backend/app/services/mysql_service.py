import pymysql
from typing import List, Any, Dict
from backend.app.core.exceptions import BusinessException
from backend.app.core.config import settings


class MySQLService:

    def __init__(self):
        self.conn = self.get_conn()

    def get_conn(self) -> pymysql.Connection:
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

    def search_poetry_ids_by_keyword(
        self,
        keyword: str,
        limit: int,
    ) -> List[int]:
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
