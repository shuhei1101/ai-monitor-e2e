"""タスクのドメインロジック。"""
from __future__ import annotations

from tasks.errors import TaskNotFoundError, ValidationError
from tasks.models import Task

TITLE_MIN_LENGTH = 1
TITLE_MAX_LENGTH = 100
CONTENT_MAX_LENGTH = 1000


def get_task(store: dict[str, Task], task_id: str) -> Task:
    """ストアからタスクを 1 件取得する。"""
    # 未登録の ID は例外にする
    if task_id not in store:
        raise TaskNotFoundError(f"task not found: {task_id}")
    return store[task_id]


def update_task(store: dict[str, Task], task_id: str, title: str, content: str = "") -> Task:
    """登録済みタスクのタイトルと本文を更新して返す。"""
    # タイトルを検証する
    if not (TITLE_MIN_LENGTH <= len(title) <= TITLE_MAX_LENGTH):
        raise ValidationError(
            f"title は {TITLE_MIN_LENGTH} 文字以上 {TITLE_MAX_LENGTH} 文字以内"
        )
    # 本文を検証する
    if len(content) > CONTENT_MAX_LENGTH:
        raise ValidationError(f"content は {CONTENT_MAX_LENGTH} 文字以内")
    # 対象タスクを取得する
    task = get_task(store, task_id)
    # 差し替えたタスクを書き戻して返す
    updated = Task(id=task.id, title=title, content=content)
    store[task_id] = updated
    return updated


def list_tasks(store: dict[str, Task]) -> list[Task]:
    """ストアのタスクを ID 順で一覧にする。"""
    return [store[key] for key in sorted(store)]
