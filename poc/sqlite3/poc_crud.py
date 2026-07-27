"""sqlite3 で CRUD 一連（作成 → 書き込み → 取得 → 更新 → 削除）が通ることを検証する。"""

from __future__ import annotations

import logging
import sqlite3
import tempfile
from pathlib import Path

from _schema import INSERT_TASK, connect_with_schema, find_task

logger = logging.getLogger(__name__)

TASK_ID = "t1"
INITIAL_TITLE = "買い物へ行く"
INITIAL_PRIORITY = 3
UPDATED_TITLE = "買い物へ行く（更新後）"
UPDATED_PRIORITY = 1


def run_crud(db_path: Path) -> None:
    """DB ファイルの新規作成から行の削除確認までを 1 本で通す。"""
    # 作成: connect した時点で DB ファイルが生成される
    conn = connect_with_schema(db_path)
    logger.info("[作成] DB ファイル=%s 存在=%s", db_path.name, db_path.exists())

    # 書き込み: commit を呼ぶまで永続化されない
    conn.execute(INSERT_TASK, (TASK_ID, INITIAL_TITLE, INITIAL_PRIORITY, None))
    conn.commit()
    logger.info("[書き込み] INSERT 1 件 commit 済み")

    # 取得: 書き込んだ行が主キーで引けるか
    logger.info("[取得] %s", find_task(conn, TASK_ID))

    # 更新: タイトルと優先度を差し替える
    conn.execute(
        "UPDATE tasks SET title = ?, priority = ? WHERE id = ?",
        (UPDATED_TITLE, UPDATED_PRIORITY, TASK_ID),
    )
    conn.commit()
    logger.info("[更新] %s", find_task(conn, TASK_ID))

    # 削除: 削除後は同じ主キーで引いても None になる
    conn.execute("DELETE FROM tasks WHERE id = ?", (TASK_ID,))
    conn.commit()
    logger.info("[削除] 削除後の取得結果=%s", find_task(conn, TASK_ID))

    conn.close()


def main() -> None:
    """一時ディレクトリに DB ファイルを作って CRUD 検証を実行する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("sqlite_version=%s", sqlite3.sqlite_version)
    with tempfile.TemporaryDirectory() as tmp_dir:
        run_crud(Path(tmp_dir) / "tasks.db")


if __name__ == "__main__":
    main()
