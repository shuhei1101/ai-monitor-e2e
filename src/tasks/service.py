"""タスクのドメインロジック。"""
from __future__ import annotations

from datetime import datetime, timezone

from tasks.errors import TaskNotFoundError, ValidationError
from tasks.models import Task


def get_task(store: dict[str, Task], task_id: str) -> Task:
    """ストアからタスクを 1 件取得する。"""
    # 未登録の ID は例外にする
    if task_id not in store:
        raise TaskNotFoundError(f"task not found: {task_id}")
    return store[task_id]


def update_task(store: dict[str, Task], task_id: str, title: str, content: str = "") -> Task:
    """登録済みタスクのタイトルと本文を更新して返す。"""
    # タイトルを検証する
    if not (1 <= len(title) <= 100):
        raise ValidationError("title は 1 文字以上 100 文字以内")
    # 本文を検証する
    if len(content) > 1000:
        raise ValidationError("content は 1000 文字以内")
    # 対象タスクを取得する
    task = get_task(store, task_id)
    # 差し替えたタスクを書き戻して返す
    updated = Task(
        id=task.id,
        title=title,
        content=content,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    store[task_id] = updated
    return updated
