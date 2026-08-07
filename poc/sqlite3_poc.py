"""sqlite3 の PoC（インメモリ DB の CRUD / 一括挿入 / 型の往復 / ロールバック）。"""
from __future__ import annotations

import sqlite3
import time


def _connect() -> sqlite3.Connection:
    """検証用のインメモリ DB を作る。"""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, content TEXT)")
    return conn


def check_crud() -> str:
    """作成 → 挿入 → 取得 → 更新 → 削除 の一連を実行する。"""
    conn = _connect()
    conn.execute("INSERT INTO tasks VALUES (?, ?, ?)", ("t1", "買い物", "牛乳"))
    title = conn.execute("SELECT title FROM tasks WHERE id = ?", ("t1",)).fetchone()[0]
    conn.execute("UPDATE tasks SET title = ? WHERE id = ?", ("買い出し", "t1"))
    conn.execute("DELETE FROM tasks WHERE id = ?", ("t1",))
    remaining = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    return f"取得={title} 削除後件数={remaining}"


def check_bulk_insert() -> str:
    """1000 件の一括挿入にかかる時間を測る。"""
    conn = _connect()
    rows = [(f"t{i}", f"タイトル{i}", "") for i in range(1000)]
    started = time.perf_counter()
    conn.executemany("INSERT INTO tasks VALUES (?, ?, ?)", rows)
    elapsed = time.perf_counter() - started
    return f"{elapsed:.3f} 秒"


def check_rollback() -> str:
    """例外発生時に rollback() で挿入前の状態へ戻ることを確認する。"""
    conn = _connect()
    conn.execute("INSERT INTO tasks VALUES (?, ?, ?)", ("t1", "買い物", "牛乳"))
    conn.commit()  # ここまでを確定させ、ロールバックの戻り先にする
    before = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    try:
        conn.execute("INSERT INTO tasks VALUES (?, ?, ?)", ("t2", "掃除", ""))
        # 主キー重複でトランザクションの途中に例外を起こす
        conn.execute("INSERT INTO tasks VALUES (?, ?, ?)", ("t1", "重複", ""))
    except sqlite3.IntegrityError:
        conn.rollback()
    after = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    return f"例外前={before} 件 ロールバック後={after} 件"


if __name__ == "__main__":
    print(check_crud())
    print(check_bulk_insert())
    print(check_rollback())
