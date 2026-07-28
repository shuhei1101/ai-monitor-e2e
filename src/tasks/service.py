from __future__ import annotations

from dataclasses import replace

from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.query import _validate_task_id
from src.tasks.types import Task, TaskStore

# タイトルの最小長
TITLE_MIN_LENGTH: int = 1
# タイトルの最大長
TITLE_MAX_LENGTH: int = 100
# 本文の最大長
CONTENT_MAX_LENGTH: int = 1000


def update_task(store: TaskStore, task_id: str, title: str, content: str) -> Task:
    """識別子を指定してタスクのタイトル・本文を更新する。"""
    # 識別子の長さを検証する
    _validate_task_id(task_id)
    # タイトルの長さを検証する
    _validate_title(title)
    # 本文の長さを検証する
    _validate_content(content)
    # 保管先に識別子が存在しなければ TaskNotFoundError を送出する
    if task_id not in store:
        raise TaskNotFoundError(f"タスクが見つかりません: {task_id}")
    # 保管先のタスクのタイトル・本文を差し替えた新しいタスクを作る
    updated = replace(store[task_id], title=title, content=content)
    # 保管先の該当エントリを新しいタスクに置き換えて、そのタスクを返す
    store[task_id] = updated
    return updated


def _validate_title(title: str) -> None:
    """タイトルの長さが許容範囲内かを検証する。"""
    # タイトルの長さが許容範囲外なら ValidationError を送出する
    if not (TITLE_MIN_LENGTH <= len(title) <= TITLE_MAX_LENGTH):
        raise ValidationError(f"title は {TITLE_MIN_LENGTH} 文字以上 {TITLE_MAX_LENGTH} 文字以内")


def _validate_content(content: str) -> None:
    """本文の長さが許容範囲内かを検証する。"""
    # 本文の長さが上限を超えていれば ValidationError を送出する
    if len(content) > CONTENT_MAX_LENGTH:
        raise ValidationError(f"content は {CONTENT_MAX_LENGTH} 文字以内")
