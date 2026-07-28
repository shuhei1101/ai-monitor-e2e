from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskEditView:
    """タスク編集画面が表示している内容。"""

    task_id: str
    initial_title: str
    initial_content: str
    title: str
    content: str
    confirm_message: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ListNavigation:
    """編集を中止したときの遷移先。"""

    screen_id: str


# 中止操作の結果(一覧への遷移 or 編集画面の表示状態)
type CancelResult = ListNavigation | TaskEditView
