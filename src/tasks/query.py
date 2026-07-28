from __future__ import annotations

from src.tasks.types import Task, TaskStore


def list_tasks(store: TaskStore) -> list[Task]:
    """登録されているタスクを識別子の昇順で全件返す。"""
    # 保管先のキーを昇順に整列する
    sorted_ids = sorted(store.keys())
    # 整列したキーの順にタスクを取り出して配列にして返す
    return [store[task_id] for task_id in sorted_ids]
