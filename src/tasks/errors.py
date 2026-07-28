from __future__ import annotations


class TaskNotFoundError(Exception):
    """指定した識別子のタスクが保管先に存在しないことを表す例外。"""


class ValidationError(Exception):
    """入力値が制約を満たさないことを表す例外。"""
