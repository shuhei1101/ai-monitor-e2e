"""PoC 各スクリプトが共有する DB セットアップ。"""
from __future__ import annotations

import logging
import sqlite3

TASKS_DDL = """
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    priority INTEGER
)
"""

INSERT_TASK_SQL = "INSERT INTO tasks (id, title, content, priority) VALUES (?, ?, ?, ?)"


def open_memory_db() -> sqlite3.Connection:
    """tasks テーブルを作成済みのインメモリ DB を開く。"""
    conn = sqlite3.connect(":memory:")
    conn.execute(TASKS_DDL)
    return conn


def build_logger(name: str) -> logging.Logger:
    """PoC の実測値を標準出力へ流すロガーを作る。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    return logging.getLogger(name)
