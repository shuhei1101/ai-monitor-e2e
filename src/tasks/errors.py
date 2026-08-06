"""タスクドメインの例外。"""
from __future__ import annotations


class TaskNotFoundError(Exception):
    """指定 ID のタスクが存在しない。"""


class ValidationError(Exception):
    """入力値が制約を満たさない。"""
