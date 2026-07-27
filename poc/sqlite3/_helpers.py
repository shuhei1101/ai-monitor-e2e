"""sqlite3 PoC の 3 本で共有するスキーマ・SQL・ログ設定。"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

# タスク永続化に必要な最小スキーマ。本番想定のカラム型で計測するため PoC 3 本で共有する
CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    priority INTEGER NOT NULL,
    note TEXT
)
"""

INSERT_TASK = "INSERT INTO tasks (id, title, priority, note) VALUES (?, ?, ?, ?)"
SELECT_TASK = "SELECT id, title, priority, note FROM tasks WHERE id = ?"


def open_tasks_db(db_path: Path) -> sqlite3.Connection:
    """tasks テーブルを用意したファイル DB の接続を開く。"""
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TASKS_TABLE)
    conn.commit()
    return conn


def setup_logging() -> None:
    """実測値をそのまま読めるようメッセージのみを出すログ設定。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
