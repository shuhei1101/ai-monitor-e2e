"""sqlite3 の PoC（インメモリ DB の CRUD / 一括挿入の性能 / 型の往復）。"""
from __future__ import annotations

import logging
import sqlite3
import time

logger = logging.getLogger(__name__)

# 一括挿入の性能を測るときに投入する件数
BULK_INSERT_COUNT = 1000

_CREATE_TABLE_SQL = """
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    priority INTEGER,
    due_date TEXT
)
"""
_INSERT_SQL = "INSERT INTO tasks VALUES (?, ?, ?, ?, ?)"


def connect_memory_db() -> sqlite3.Connection:
    """検証用のインメモリ DB を作り、tasks テーブルを用意する。"""
    conn = sqlite3.connect(":memory:")
    conn.execute(_CREATE_TABLE_SQL)
    return conn


def check_crud() -> str:
    """作成 → 挿入 → 取得 → 更新 → 削除 の一連を実行して実測値を返す。"""
    conn = connect_memory_db()
    conn.execute(_INSERT_SQL, ("t1", "買い物", "牛乳", 1, None))
    inserted = conn.execute("SELECT title FROM tasks WHERE id = ?", ("t1",)).fetchone()[0]
    conn.execute("UPDATE tasks SET title = ? WHERE id = ?", ("買い出し", "t1"))
    updated = conn.execute("SELECT title FROM tasks WHERE id = ?", ("t1",)).fetchone()[0]
    conn.execute("DELETE FROM tasks WHERE id = ?", ("t1",))
    remaining = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    return f"挿入後={inserted} 更新後={updated} 削除後件数={remaining}"


def check_bulk_insert() -> str:
    """BULK_INSERT_COUNT 件の一括挿入にかかる時間を測る。"""
    conn = connect_memory_db()
    rows = [(f"t{i}", f"タイトル{i}", "", i, None) for i in range(BULK_INSERT_COUNT)]
    started = time.perf_counter()
    conn.executemany(_INSERT_SQL, rows)
    conn.commit()
    elapsed = time.perf_counter() - started
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    return f"{count} 件を {elapsed:.3f} 秒で挿入"


def check_type_roundtrip() -> str:
    """str / int / None が挿入時と同じ型で取り出せるかを確認する。"""
    conn = connect_memory_db()
    conn.execute(_INSERT_SQL, ("t1", "買い物", "牛乳", 3, None))
    title, priority, due_date = conn.execute(
        "SELECT title, priority, due_date FROM tasks WHERE id = ?", ("t1",)
    ).fetchone()
    return (
        f"title={type(title).__name__}({title!r}) "
        f"priority={type(priority).__name__}({priority!r}) "
        f"due_date={type(due_date).__name__}({due_date!r})"
    )


def main() -> None:
    """3 観点の検証を順に実行して実測値をログへ出す。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("インメモリ DB の CRUD: %s", check_crud())
    logger.info("一括挿入の性能: %s", check_bulk_insert())
    logger.info("型の往復: %s", check_type_roundtrip())


if __name__ == "__main__":
    main()
