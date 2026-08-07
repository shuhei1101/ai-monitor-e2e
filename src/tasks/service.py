"""タスクのドメインロジック。"""
from __future__ import annotations

from dataclasses import replace

from tasks.errors import TaskNotFoundError, ValidationError
from tasks.models import Task

TITLE_MAX_LENGTH = 100
CONTENT_MAX_LENGTH = 1000


def get_task(store: dict[str, Task], task_id: str) -> Task:
    """ストアからタスクを 1 件取得する。"""
    # 未登録の ID は例外にする
    if task_id not in store:
        raise TaskNotFoundError(f"task not found: {task_id}")
    return store[task_id]


def update_task(
    store: dict[str, Task], task_id: str, title: str, content: str = ""
) -> Task:
    """登録済みタスクのタイトルと本文を更新して返す。"""
    # 1. title を検証する（空文字 or 100 文字超なら ValidationError）
    if not title or len(title) > TITLE_MAX_LENGTH:
        raise ValidationError(f"title は 1 文字以上 {TITLE_MAX_LENGTH} 文字以内")
    # 2. content を検証する（1000 文字超なら ValidationError）
    if len(content) > CONTENT_MAX_LENGTH:
        raise ValidationError(f"content は {CONTENT_MAX_LENGTH} 文字以内")
    # 3. store から task_id のタスクを取得する（無ければ TaskNotFoundError）
    task = get_task(store, task_id)
    # 4. タイトルと本文を差し替えたタスクを store に書き戻して返す
    updated = replace(task, title=title, content=content)
    store[task_id] = updated
    return updated
