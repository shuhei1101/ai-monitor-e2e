"""インメモリ DB で 作成 → 挿入 → 取得 → 更新 → 削除 が一連で通るかを検証する。"""
from __future__ import annotations

import sqlite3

from _schema import INSERT_TASK_SQL, build_logger, open_memory_db

TASK_ID = "t1"
INITIAL_PRIORITY = 1

logger = build_logger(__name__)


def _find_title(conn: sqlite3.Connection, task_id: str) -> str | None:
    """タスクのタイトルを取得する（未登録なら None）。"""
    row = conn.execute("SELECT title FROM tasks WHERE id = ?", (task_id,)).fetchone()
    # 削除後の取得を検証したいので、行なしは例外にせず None を返す
    if row is None:
        return None
    return row[0]


def main() -> None:
    """CRUD を順に流して各段階の取得結果をログへ出す。"""
    conn = open_memory_db()
    logger.info("CREATE TABLE: 成功")

    conn.execute(INSERT_TASK_SQL, (TASK_ID, "買い物", "牛乳", INITIAL_PRIORITY))
    logger.info(f"INSERT 後の SELECT: {_find_title(conn, TASK_ID)}")

    conn.execute("UPDATE tasks SET title = ? WHERE id = ?", ("買い物リスト", TASK_ID))
    logger.info(f"UPDATE 後の SELECT: {_find_title(conn, TASK_ID)}")

    conn.execute("DELETE FROM tasks WHERE id = ?", (TASK_ID,))
    logger.info(f"DELETE 後の SELECT: {_find_title(conn, TASK_ID)}")

    conn.close()


if __name__ == "__main__":
    main()
