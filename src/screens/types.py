from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.tasks.types import Task


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskRow:
    """タスク一覧の 1 行が持つ表示値。"""

    id: str
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskListView:
    """タスク一覧画面が表示している内容。"""

    rows: list[TaskRow]
    empty_message: str | None = None
    not_found_message: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class EditDestination:
    """編集画面の遷移先を、URL 文字列にする前の形で表したもの。"""

    screen_id: str
    task_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EditNavigation:
    """編集画面へ遷移するときに引き渡す一式(遷移先 + 初期表示値)。"""

    destination: EditDestination
    url: str
    title: str
    content: str


# 行選択の結果(遷移する場合は編集画面遷移、遷移しない場合は一覧の表示状態)
type RowSelectionResult = EditNavigation | TaskListView

# タスク一覧を取得する関数のシグネチャ。実装はバックエンドの list_tasks
type ListTasks = Callable[[], list[Task]]

# タスク 1 件の詳細を取得する関数のシグネチャ。実装はバックエンドの get_task
type GetTask = Callable[[str], Task]
