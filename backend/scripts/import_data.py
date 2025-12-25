from __future__ import annotations

import json
import glob
import re
import os
from typing import Iterable, List, Dict, Any, Tuple

import pymysql
import requests
from tqdm import tqdm
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)

# =========================
# 基础配置
# =========================

MYSQL_CONFIG: Dict[str, str] = {
    "host": "localhost",
    "port": "3306",
    "user": "poem",
    "password": "poem123456",
    "database": "shiyun_db",
    "charset": "utf8mb4",
}

OLLAMA_EMBEDDING_URL: str = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL: str = "nomic-embed-text"
EMBEDDING_DIM: int = 768

MILVUS_HOST: str = "localhost"
MILVUS_PORT: int = 19530
MILVUS_COLLECTION: str = "poetry_embedding"

DATA_ROOT: str = "../../database/chinese-gushiwen"

DEFAULT_WRITER_ID: int = 1
DEFAULT_POETRY_ID: int = 1

# =========================
# MySQL
# =========================


def get_mysql_conn() -> pymysql.Connection:
    return pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=int(MYSQL_CONFIG["port"]),
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset=MYSQL_CONFIG["charset"],
    )


# =========================
# Milvus
# =========================


def init_milvus() -> Collection:
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

    if utility.has_collection(MILVUS_COLLECTION):
        collection = Collection(MILVUS_COLLECTION)
        collection.load()
        return collection

    fields = [
        FieldSchema(
            name="poetry_id",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=False,
        ),
        FieldSchema(
            name="embedding",
            dtype=DataType.FLOAT_VECTOR,
            dim=EMBEDDING_DIM,
        ),
    ]

    schema = CollectionSchema(
        fields=fields,
        description="Poetry semantic embedding",
    )

    collection = Collection(
        name=MILVUS_COLLECTION,
        schema=schema,
    )

    res = collection.create_index(
        field_name="embedding",
        index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "IP",
            "params": {
                "nlist": 1024
            },
        },
    )

    collection.load()
    return collection


# =========================
# 工具函数
# =========================


def iter_json_files(pattern: str) -> Iterable[Dict[str, Any]]:
    for file_path in glob.glob(pattern):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            decoder = json.JSONDecoder()
            idx = 0
            length = len(content)

            while idx < length:
                content = content.lstrip()
                try:
                    obj, offset = decoder.raw_decode(content)
                    yield obj
                    content = content[offset:]
                except json.JSONDecodeError:
                    break


def get_embedding(text: str) -> list[float] | None:
    payload = {
        "model": "nomic-embed-text",
        "prompt": text,
    }

    try:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json=payload,
            timeout=60,
        )

        if resp.status_code != 200:
            print("embedding failed:", resp.text)
            return None

        data = resp.json()
        embedding = data.get("embedding")

        if not embedding:
            return None

        # nomic-embed-text 固定 768 维
        if len(embedding) != 768:
            print("embedding dim mismatch:", len(embedding))
            return None

        return embedding

    except requests.RequestException as e:
        print("embedding exception:", e)
        return None


def poetry_exists(conn: pymysql.Connection, title: str,
                  writer_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1 FROM poetry
        WHERE title = %s AND writer_id = %s
        LIMIT 1
        """,
        (title, writer_id),
    )
    return cursor.fetchone() is not None


def poetry_has_embedding(conn: pymysql.Connection, poetry_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT milvus_id FROM poetry WHERE id = %s",
        (poetry_id, ),
    )
    row = cursor.fetchone()
    return bool(row and row[0])


def parse_from(from_text: str) -> Tuple[str, str]:
    """
    解析 '佚名《越人歌》' → ('佚名', '越人歌')
    """
    FROM_PATTERN = re.compile(r"^(?P<author>[^《]+)《(?P<title>[^》]+)》$")
    if not from_text:
        return "佚名", "佚名"

    m = FROM_PATTERN.match(from_text.strip())
    if not m:
        print(f"Unrecognized from format: {from_text}")
        return "佚名", from_text

    return m.group("author"), m.group("title")


def get_or_create_poetry(cur, title: str, writer_id: int) -> int:
    cur.execute("SELECT id FROM poetry WHERE title = %s AND writer_id = %s",
                (title, writer_id))
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO poetry (title, writer_id, content)
        VALUES (%s, %s, %s)
        """, (title, writer_id, "此诗暂无全文，仅收录名句。"))
    return cur.lastrowid


# =========================
# 1. 导入作者
# =========================


def import_writers(conn: pymysql.Connection) -> None:
    cursor = conn.cursor()

    writer_files = os.path.join(DATA_ROOT, "writer", "*.json")

    for w in iter_json_files(writer_files):
        name: str = w.get("name", "").strip()
        if not name:
            continue

        intro: str = w.get("simpleIntro", "")
        detail_intro: str = w.get("detailIntro", "")
        cursor.execute(
            "SELECT id FROM writer WHERE name=%s",
            (name, ),
        )
        if cursor.fetchone():
            # print("error: writer repeat")
            continue

        cursor.execute(
            "INSERT INTO writer (name, intro, detail_intro) VALUES (%s, %s, %s)",
            (name, intro, detail_intro),
        )

    conn.commit()
    cursor.close()


# =========================
# 2. 导入诗词 + 向量
# =========================


def import_poetry(
    conn: pymysql.Connection,
    collection: Collection,
) -> None:
    cursor = conn.cursor()

    guwen_files = os.path.join(DATA_ROOT, "guwen", "*.json")

    commit_count = 0
    for g in tqdm(list(iter_json_files(guwen_files)), desc="Import poetry"):
        title: str = g.get("title", "佚名")
        content: str = g.get("content", "")
        dynasty: str = g.get("dynasty", "")
        writer_name: str = g.get("writer", "佚名")
        keywords: str = ",".join(g.get("type", []))
        translation: str = g.get("translation", "")
        connotation: str = g.get("remark", "")
        remark: str = g.get("shangxi", "")

        # 查作者
        cursor.execute(
            "SELECT id FROM writer WHERE name=%s",
            (writer_name, ),
        )
        row = cursor.fetchone()
        writer_id: int = row[0] if row else DEFAULT_WRITER_ID

        if poetry_exists(conn, title, writer_id):
            continue  # 已导入，直接跳过

        cursor.execute(
            """
            INSERT INTO poetry (title, content, dynasty, writer_id, keywords, connotation, translation, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (title, content, dynasty, writer_id, keywords, connotation,
             translation, remark),
        )
        poetry_id: int = cursor.lastrowid

        embed_text = "\n".join(part for part in [
            title,
            content,
            g.get("translation", ""),
            g.get("shangxi", ""),
        ] if part)

        embedding = get_embedding(embed_text[0:800])

        mr = collection.insert([
            [poetry_id],
            [embedding],
        ])
        milvus_id = mr.primary_keys[0]
        cursor.execute(
            "UPDATE poetry SET milvus_id = %s WHERE id = %s",
            (str(milvus_id), poetry_id),
        )
        commit_count += 1
        if commit_count >= 10:
            commit_count = 0
            conn.commit()
            collection.flush()

    conn.commit()
    collection.flush()
    cursor.close()


# =========================
# 3. 导入名句
# =========================


def import_sentences(conn: pymysql.Connection) -> None:
    cursor = conn.cursor()

    sentence_file = os.path.join(
        DATA_ROOT,
        "sentence",
        "sentence1-10000.json",
    )

    # 已存在句子（防止重复导入）
    cursor.execute("SELECT content FROM sentence")
    existing = {r[0] for r in cursor.fetchall()}

    commit_count = 0
    for g in tqdm(list(iter_json_files(sentence_file)),
                  desc="Import sentence"):
        content: str = g.get("name", "").strip()
        writer, title = parse_from(g.get("from", ""))
        if not content or content in existing:
            continue

        # 查找作者
        cursor.execute("SELECT id FROM writer WHERE name = %s", (writer, ))
        row = cursor.fetchone()
        writer_id = DEFAULT_WRITER_ID
        if row:
            writer_id = row[0]
        # 查找诗文
        poetry_id = get_or_create_poetry(cursor, title, writer_id)

        cursor.execute(
            "INSERT INTO sentence (content, poetry_id) VALUES (%s, %s)",
            (content, poetry_id),
        )

        commit_count += 1
        if commit_count >= 100:
            conn.commit()
            commit_count = 0

    conn.commit()
    cursor.close()


# =========================
# 主入口
# =========================


def main() -> None:
    conn = get_mysql_conn()
    collection = init_milvus()

    # 已完成
    # print("▶ 导入作者")
    # import_writers(conn)

    # 已完成
    # print("▶ 导入诗词并生成向量")
    # import_poetry(conn, collection)

    # 已完成
    print("▶ 导入名句")
    import_sentences(conn)

    conn.close()
    print("✔ 数据导入完成")


if __name__ == "__main__":
    main()
