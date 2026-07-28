from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """タスク 1 件を表す不変 DTO。"""

    id: str
    title: str
    content: str = ""


# 識別子をキーにタスクを保持する保管先の型
type TaskStore = dict[str, Task]
