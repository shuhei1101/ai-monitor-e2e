from __future__ import annotations

import logging

from src.screens.navigation import resolve_edit_destination, to_url
from src.screens.types import (
    EditNavigation,
    GetTask,
    ListTasks,
    RowSelectionResult,
    TaskListView,
    TaskRow,
)
from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.types import Task

logger = logging.getLogger(__name__)

# 空状態メッセージ
EMPTY_MESSAGE: str = "タスクがありません"
# 未検出メッセージ
NOT_FOUND_MESSAGE: str = "タスクが見つかりません"


def _build_view(tasks: list[Task], *, not_found_message: str | None) -> TaskListView:
    """取得したタスクからタスク一覧画面の表示状態を組み立てる。"""
    # タスクを識別子とタイトルだけのタスク行へ移す
    rows = [TaskRow(id=task.id, title=task.title) for task in tasks]
    # 空状態メッセージを決める
    if not rows:
        # 行が 0 件の場合、EMPTY_MESSAGE を入れる
        empty_message = EMPTY_MESSAGE
    else:
        # 行が 1 件以上の場合、None を入れる
        empty_message = None
    # 行・空状態メッセージ・受け取った未検出メッセージから表示状態を組み立てて返す
    return TaskListView(
        rows=rows,
        empty_message=empty_message,
        not_found_message=not_found_message,
    )


def render_task_list(*, list_tasks: ListTasks) -> TaskListView:
    """タスク一覧を取得して表示状態を返す。"""
    # 一覧取得を呼んでタスクを得る
    tasks = list_tasks()
    # 得たタスクから表示状態を組み立てて返す
    return _build_view(tasks, not_found_message=None)


def select_task_row(
    task_id: str, *, get_task: GetTask, list_tasks: ListTasks
) -> RowSelectionResult:
    """タスク行の選択を処理し、編集画面への遷移か一覧の再表示を返す。"""
    # 識別子から遷移先を決める
    destination = resolve_edit_destination(task_id)
    try:
        # 詳細取得を呼んで対象タスクを得る
        task = get_task(task_id)
    except (TaskNotFoundError, ValidationError):
        # 見つからない、または識別子の形式が不正な場合、一覧を取得し直して未検出メッセージ付きの表示状態を返す
        logger.warning("選択したタスクの詳細を取得できなかった: %s", task_id)
        return _build_view(list_tasks(), not_found_message=NOT_FOUND_MESSAGE)
    # 遷移先を URL 文字列に変換する
    url = to_url(destination)
    # 遷移先・URL・取得したタイトル・本文から編集画面遷移を組み立てて返す
    return EditNavigation(
        destination=destination,
        url=url,
        title=task.title,
        content=task.content,
    )
