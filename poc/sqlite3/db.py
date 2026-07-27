"""sqlite3 によるタスクの永続化操作。"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable

from poc.sqlite3.types import Task, TaskId

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    priority INTEGER NOT NULL,
    memo TEXT
)
"""
INSERT_SQL = "INSERT INTO tasks (id, title, priority, memo) VALUES (?, ?, ?, ?)"
SELECT_SQL = "SELECT id, title, priority, memo FROM tasks WHERE id = ?"
UPDATE_SQL = "UPDATE tasks SET title = ?, priority = ?, memo = ? WHERE id = ?"
DELETE_SQL = "DELETE FROM tasks WHERE id = ?"
COUNT_SQL = "SELECT COUNT(*) FROM tasks"


def connect(db_path: str) -> sqlite3.Connection:
    """DB へ接続し、tasks テーブルを用意した接続を返す。"""
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    return conn


def create_task(conn: sqlite3.Connection, task: Task) -> Task:
    """タスクを 1 件登録して commit する。"""
    conn.execute(INSERT_SQL, _to_row(task))
    conn.commit()
    return task


def create_tasks(conn: sqlite3.Connection, tasks: Iterable[Task]) -> None:
    """複数タスクを executemany + 単一 commit で一括登録する。"""
    conn.executemany(INSERT_SQL, [_to_row(task) for task in tasks])
    conn.commit()


def find_task(conn: sqlite3.Connection, task_id: TaskId) -> Task | None:
    """id でタスクを 1 件検索する。存在しなければ None を返す。"""
    row = conn.execute(SELECT_SQL, (task_id,)).fetchone()
    if row is None:
        return None
    return _to_task(row)


def update_task(conn: sqlite3.Connection, task: Task) -> Task | None:
    """タスクの title / priority / memo を上書きする。対象が無ければ None を返す。"""
    cursor = conn.execute(UPDATE_SQL, (task.title, task.priority, task.memo, task.id))
    conn.commit()
    # 更新行数 0 = 該当 id のレコードが存在しない
    if cursor.rowcount == 0:
        return None
    return task


def delete_task(conn: sqlite3.Connection, task_id: TaskId) -> None:
    """タスクを 1 件削除する。"""
    conn.execute(DELETE_SQL, (task_id,))
    conn.commit()


def count_tasks(conn: sqlite3.Connection) -> int:
    """登録済みタスクの件数を返す。"""
    count: int = conn.execute(COUNT_SQL).fetchone()[0]
    return count


def _to_row(task: Task) -> tuple[str, str, int, str | None]:
    """Task を INSERT のパラメータ列に変換する。"""
    return (task.id, task.title, task.priority, task.memo)


def _to_task(row: tuple[str, str, int, str | None]) -> Task:
    """SELECT の 1 行を Task に変換する。"""
    return Task(id=row[0], title=row[1], priority=row[2], memo=row[3])
