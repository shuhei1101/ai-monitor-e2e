"""sqlite3 の PoC 検証。3 観点の実測値をログへ出す。"""
from __future__ import annotations

import logging
import sqlite3
import time

logger = logging.getLogger(__name__)

BULK_INSERT_ROWS = 1000
CREATE_TASKS_TABLE = "CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, content TEXT)"
INSERT_TASK = "INSERT INTO tasks VALUES (?, ?, ?)"
COUNT_TASKS = "SELECT COUNT(*) FROM tasks"


def _open_tasks_db() -> sqlite3.Connection:
    """tasks テーブルを持つインメモリ DB を開く。"""
    conn = sqlite3.connect(":memory:")
    conn.execute(CREATE_TASKS_TABLE)
    return conn


def verify_crud() -> None:
    """インメモリ DB で 作成 → 挿入 → 取得 → 更新 → 削除 を一連で通す。"""
    conn = _open_tasks_db()
    try:
        conn.execute(INSERT_TASK, ("t1", "買い物", "牛乳を買う"))
        inserted = conn.execute("SELECT title, content FROM tasks WHERE id = ?", ("t1",)).fetchone()
        conn.execute("UPDATE tasks SET title = ? WHERE id = ?", ("買い出し", "t1"))
        updated = conn.execute("SELECT title, content FROM tasks WHERE id = ?", ("t1",)).fetchone()
        conn.execute("DELETE FROM tasks WHERE id = ?", ("t1",))
        remaining = conn.execute(COUNT_TASKS).fetchone()[0]
    finally:
        conn.close()
    logger.info("CRUD: 挿入=%s 更新後=%s 削除後の件数=%s", inserted, updated, remaining)


def verify_bulk_insert() -> None:
    """1000 件の一括挿入にかかる秒数を測る。"""
    conn = _open_tasks_db()
    rows = [(f"t{i}", f"タスク{i}", "本文") for i in range(BULK_INSERT_ROWS)]
    try:
        started = time.perf_counter()
        conn.executemany(INSERT_TASK, rows)
        conn.commit()
        elapsed = time.perf_counter() - started
        inserted_count = conn.execute(COUNT_TASKS).fetchone()[0]
    finally:
        conn.close()
    logger.info("一括挿入: %s 件 / %.4f 秒", inserted_count, elapsed)


def verify_type_roundtrip() -> None:
    """str / int / None が挿入時と同じ型で取り出せるかを確認する。"""
    samples: dict[str, object] = {"str": "買い物", "int": 42, "none": None}
    conn = sqlite3.connect(":memory:")
    try:
        # value 列は型宣言なし（SQLite の動的型に任せて型指定の影響を除く）
        conn.execute("CREATE TABLE samples (key TEXT PRIMARY KEY, value)")
        conn.executemany("INSERT INTO samples VALUES (?, ?)", list(samples.items()))
        for key, original in samples.items():
            (restored,) = conn.execute(
                "SELECT value FROM samples WHERE key = ?", (key,)
            ).fetchone()
            same = type(restored) is type(original) and restored == original
            logger.info(
                "型の往復: %s 挿入=%r(%s) 取得=%r(%s) 一致=%s",
                key,
                original,
                type(original).__name__,
                restored,
                type(restored).__name__,
                same,
            )
    finally:
        conn.close()


def main() -> None:
    """3 観点の検証をまとめて実行する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    verify_crud()
    verify_bulk_insert()
    verify_type_roundtrip()


if __name__ == "__main__":
    main()
