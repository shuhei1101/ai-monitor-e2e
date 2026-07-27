"""tasks テーブルに対する CRUD（作成 → 書き込み → 取得 → 更新 → 削除）を一連で検証する。"""

from __future__ import annotations

import logging
import sqlite3
import tempfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from _helpers import INSERT_TASK, SELECT_TASK, open_tasks_db, setup_logging

logger = logging.getLogger(__name__)

TASK_ID = "t1"
INITIAL_TITLE = "買い物に行く"
INITIAL_PRIORITY = 3
UPDATED_TITLE = "買い物に行く（牛乳を追加）"
UPDATED_PRIORITY = 1
PERSISTED_TASK_ID = "t2"
PERSISTED_TITLE = "再接続で読めるか確認する"
PERSISTED_PRIORITY = 2


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """tasks テーブルの 1 行。"""

    id: str
    title: str
    priority: int
    note: str | None


def create_task(conn: sqlite3.Connection, task: Task) -> None:
    """タスクを 1 件書き込む。"""
    with conn:  # 正常終了なら commit・例外なら rollback される
        conn.execute(INSERT_TASK, (task.id, task.title, task.priority, task.note))


def find_task(conn: sqlite3.Connection, task_id: str) -> Task | None:
    """id でタスクを 1 件取得する（該当なしは None）。"""
    row = conn.execute(SELECT_TASK, (task_id,)).fetchone()
    if row is None:
        return None
    return Task(id=row[0], title=row[1], priority=row[2], note=row[3])


def update_task(conn: sqlite3.Connection, task_id: str, *, title: str, priority: int) -> int:
    """タスクの title / priority を更新して更新件数を返す。"""
    with conn:
        cursor = conn.execute(
            "UPDATE tasks SET title = ?, priority = ? WHERE id = ?", (title, priority, task_id)
        )
    return cursor.rowcount


def delete_task(conn: sqlite3.Connection, task_id: str) -> int:
    """タスクを削除して削除件数を返す。"""
    with conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount


def _run_crud(conn: sqlite3.Connection) -> bool:
    """CRUD を順に実行し、各段階の観測値が期待どおりかを返す。"""
    created = Task(id=TASK_ID, title=INITIAL_TITLE, priority=INITIAL_PRIORITY, note=None)
    create_task(conn, created)
    after_create = find_task(conn, TASK_ID)
    logger.info(f"書き込み後の取得: {after_create}")

    updated_count = update_task(conn, TASK_ID, title=UPDATED_TITLE, priority=UPDATED_PRIORITY)
    after_update = find_task(conn, TASK_ID)
    logger.info(f"更新件数: {updated_count} / 更新後の取得: {after_update}")

    deleted_count = delete_task(conn, TASK_ID)
    after_delete = find_task(conn, TASK_ID)
    logger.info(f"削除件数: {deleted_count} / 削除後の取得: {after_delete}")

    expected_update = Task(
        id=TASK_ID, title=UPDATED_TITLE, priority=UPDATED_PRIORITY, note=None
    )
    return (
        after_create == created
        and updated_count == 1
        and after_update == expected_update
        and deleted_count == 1
        and after_delete is None
    )


def main() -> None:
    """一時ディレクトリのファイル DB に対して CRUD と再接続後の読み出しを確認する。"""
    setup_logging()
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "tasks.db"

        with closing(open_tasks_db(db_path)) as conn:
            crud_ok = _run_crud(conn)
            # 接続を閉じたあとも残るか確認するため、別 id を 1 件だけ残す
            create_task(
                conn,
                Task(
                    id=PERSISTED_TASK_ID,
                    title=PERSISTED_TITLE,
                    priority=PERSISTED_PRIORITY,
                    note=None,
                ),
            )

        # 同じファイルを開き直して、commit した行がプロセス内キャッシュ抜きで読めるかを見る
        with closing(open_tasks_db(db_path)) as reopened:
            after_reopen = find_task(reopened, PERSISTED_TASK_ID)
        logger.info(f"再接続後の取得: {after_reopen}")

    persisted_ok = after_reopen is not None and after_reopen.title == PERSISTED_TITLE
    logger.info(f"判定: {'成功' if crud_ok and persisted_ok else '失敗'}")


if __name__ == "__main__":
    main()
