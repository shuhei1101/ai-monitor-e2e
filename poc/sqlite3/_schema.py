"""PoC 3 本が共有する tasks テーブルのスキーマと接続ヘルパー。"""

from __future__ import annotations

import sqlite3
from pathlib import Path

CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id       TEXT    PRIMARY KEY,
    title    TEXT    NOT NULL,
    priority INTEGER NOT NULL,
    due_date TEXT
)
"""

INSERT_TASK = "INSERT INTO tasks (id, title, priority, due_date) VALUES (?, ?, ?, ?)"

SELECT_TASK_BY_ID = "SELECT id, title, priority, due_date FROM tasks WHERE id = ?"


def connect_with_schema(db_path: Path) -> sqlite3.Connection:
    """DB ファイルへ接続し、tasks テーブルを作成済みの接続を返す。"""
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TASKS_TABLE)
    conn.commit()
    return conn


def find_task(conn: sqlite3.Connection, task_id: str) -> tuple[str, str, int, str | None] | None:
    """主キー指定で 1 件取得する（存在しなければ None）。"""
    return conn.execute(SELECT_TASK_BY_ID, (task_id,)).fetchone()
