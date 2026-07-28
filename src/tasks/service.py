"""タスクのドメインロジック。"""
from __future__ import annotations

from tasks.errors import TaskNotFoundError
from tasks.models import Task


def get_task(store: dict[str, Task], task_id: str) -> Task:
    """ストアからタスクを 1 件取得する。"""
    # 未登録の ID は例外にする
    if task_id not in store:
        raise TaskNotFoundError(f"task not found: {task_id}")
    return store[task_id]
