import pymysql
from typing import List, Any, Dict

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
