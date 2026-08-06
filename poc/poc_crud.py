"""インメモリ DB でタスクの CRUD が一連で成立するかを実測する。"""
from __future__ import annotations

import logging

from poc.db import connect_tasks_db, setup_logger

logger = logging.getLogger(__name__)

TASK_ID = "t1"
INITIAL_TITLE = "買い物"
INITIAL_CONTENT = "牛乳"
UPDATED_TITLE = "買い物リスト"
UPDATED_CONTENT = "牛乳とパン"


def main() -> None:
    """作成 → 挿入 → 取得 → 更新 → 削除 を順に実行して各段の結果を出力する。"""
    setup_logger()

    # 作成: connect_tasks_db が CREATE TABLE まで済ませる
    conn = connect_tasks_db()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    logger.info("作成: テーブル一覧 %s", tables)

    # 挿入: プレースホルダにタプルを渡す
    inserted = conn.execute(
        "INSERT INTO tasks VALUES (?, ?, ?)", (TASK_ID, INITIAL_TITLE, INITIAL_CONTENT)
    )
    conn.commit()
    logger.info("挿入: rowcount=%s", inserted.rowcount)

    # 取得: 挿入した 1 件を主キーで引く
    row = conn.execute(
        "SELECT id, title, content FROM tasks WHERE id = ?", (TASK_ID,)
    ).fetchone()
    logger.info("取得: %s", row)

    # 更新: タイトルと本文を差し替えて取得し直す
    updated = conn.execute(
        "UPDATE tasks SET title = ?, content = ? WHERE id = ?",
        (UPDATED_TITLE, UPDATED_CONTENT, TASK_ID),
    )
    conn.commit()
    updated_row = conn.execute(
        "SELECT id, title, content FROM tasks WHERE id = ?", (TASK_ID,)
    ).fetchone()
    logger.info("更新: rowcount=%s 更新後=%s", updated.rowcount, updated_row)

    # 削除: 削除後の件数が 0 になることまで見る
    deleted = conn.execute("DELETE FROM tasks WHERE id = ?", (TASK_ID,))
    conn.commit()
    remaining = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    logger.info("削除: rowcount=%s 残件数=%s", deleted.rowcount, remaining)

    conn.close()


if __name__ == "__main__":
    main()
