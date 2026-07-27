"""タスクのドメインモデル。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """タスク 1 件。"""

    id: str
    title: str
    content: str = ""
    updated_at: str = ""
