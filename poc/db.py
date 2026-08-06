"""PoC 共通のインメモリ DB 接続。"""
from __future__ import annotations

import logging
import sqlite3

IN_MEMORY_DSN = ":memory:"
CREATE_TASKS_TABLE = """
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT
)
"""


def connect_tasks_db() -> sqlite3.Connection:
    """tasks テーブルを作成済みのインメモリ DB へ接続する。"""
    conn = sqlite3.connect(IN_MEMORY_DSN)
    conn.execute(CREATE_TASKS_TABLE)
    return conn


def setup_logger() -> None:
    """実測値をそのまま標準出力へ流すロガーを設定する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
