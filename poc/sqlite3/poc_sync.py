"""sqlite3 の同期 API を対象にした PoC（インメモリ CRUD / 一括挿入の性能 / 型の往復）。"""

from __future__ import annotations

import logging
import sqlite3
import time

logger = logging.getLogger(__name__)

# タスク永続化を想定した最小スキーマ。content は NULL 許容にして型の往復に None を含められるようにする
TASKS_DDL = """
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    priority INTEGER NOT NULL,
    content TEXT
)
"""

BULK_INSERT_COUNT = 1000  # 一括挿入の性能を測る件数


def open_memory_db() -> sqlite3.Connection:
    """インメモリ DB を開き、tasks テーブルを作成済みの接続を返す。"""
    conn = sqlite3.connect(":memory:")
    conn.execute(TASKS_DDL)
    return conn


def verify_crud() -> None:
    """作成 → 挿入 → 取得 → 更新 → 削除 を一連で実行し、各段階の結果を出力する。"""
    conn = open_memory_db()
    logger.info("[CRUD] テーブル作成: %s", conn.execute("SELECT name FROM sqlite_master").fetchall())

    conn.execute("INSERT INTO tasks VALUES (?, ?, ?, ?)", ("t1", "買い物", 1, "牛乳を買う"))
    logger.info("[CRUD] 挿入後の件数: %s", conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])

    selected = conn.execute("SELECT id, title, content FROM tasks WHERE id = ?", ("t1",)).fetchone()
    logger.info("[CRUD] 取得: %s", selected)

    conn.execute("UPDATE tasks SET title = ? WHERE id = ?", ("買い物リスト", "t1"))
    updated = conn.execute("SELECT title FROM tasks WHERE id = ?", ("t1",)).fetchone()
    logger.info("[CRUD] 更新後の title: %s", updated[0])

    conn.execute("DELETE FROM tasks WHERE id = ?", ("t1",))
    logger.info("[CRUD] 削除後の件数: %s", conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])

    conn.close()


def verify_bulk_insert() -> float:
    """executemany で BULK_INSERT_COUNT 件を挿入し、commit までの所要秒数を返す。"""
    conn = open_memory_db()
    rows = [(f"t{i}", f"タスク{i}", i % 3, f"本文{i}") for i in range(BULK_INSERT_COUNT)]

    started = time.perf_counter()
    conn.executemany("INSERT INTO tasks VALUES (?, ?, ?, ?)", rows)
    conn.commit()
    elapsed = time.perf_counter() - started

    logger.info(
        "[BULK] %s 件の挿入: %.4f 秒 / 挿入後の件数: %s",
        BULK_INSERT_COUNT,
        elapsed,
        conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
    )
    conn.close()
    return elapsed


def verify_type_roundtrip() -> None:
    """str / int / None を挿入し、取り出した値の型が挿入時と一致するかを出力する。"""
    conn = open_memory_db()
    inserted = ("t1", "買い物", 1, None)
    conn.execute("INSERT INTO tasks VALUES (?, ?, ?, ?)", inserted)
    fetched = conn.execute("SELECT id, title, priority, content FROM tasks").fetchone()

    # 列ごとに挿入時と取得時の型を突き合わせる
    for column, before, after in zip(("id", "title", "priority", "content"), inserted, fetched, strict=True):
        logger.info(
            "[TYPE] %s: %r(%s) -> %r(%s) / 一致: %s",
            column,
            before,
            type(before).__name__,
            after,
            type(after).__name__,
            type(before) is type(after),
        )

    conn.close()


def main() -> None:
    """3 つの検証を順に実行する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    verify_crud()
    verify_bulk_insert()
    verify_type_roundtrip()


if __name__ == "__main__":
    main()
