from __future__ import annotations

from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.types import Task, TaskStore

# 識別子の最小長
TASK_ID_MIN_LENGTH: int = 1
# 識別子の最大長
TASK_ID_MAX_LENGTH: int = 100


def list_tasks(store: TaskStore) -> list[Task]:
    """登録されているタスクを識別子の昇順で全件返す。"""
    # 保管先のキーを昇順に整列する
    sorted_ids = sorted(store.keys())
    # 整列したキーの順にタスクを取り出して配列にして返す
    return [store[task_id] for task_id in sorted_ids]


def get_task(store: TaskStore, task_id: str) -> Task:
    """識別子を指定してタスク 1 件を返す。"""
    # 識別子の長さを検証する
    _validate_task_id(task_id)
    # 保管先に識別子が存在しなければ TaskNotFoundError を送出する
    if task_id not in store:
        raise TaskNotFoundError(f"タスクが見つかりません: {task_id}")
    # 保管先から識別子に対応するタスクを取り出して返す
    return store[task_id]


def _validate_task_id(task_id: str) -> None:
    """識別子の長さが許容範囲内かを検証する。"""
    # 識別子の長さが許容範囲外なら ValidationError を送出する
    if not (TASK_ID_MIN_LENGTH <= len(task_id) <= TASK_ID_MAX_LENGTH):
        raise ValidationError(
            f"task_id は {TASK_ID_MIN_LENGTH} 文字以上 {TASK_ID_MAX_LENGTH} 文字以内"
        )
