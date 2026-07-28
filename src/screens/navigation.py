from __future__ import annotations

from src.screens.types import EditDestination

# 編集画面の画面識別子
TASK_EDIT_SCREEN_ID: str = "task-edit"


def resolve_edit_destination(task_id: str) -> EditDestination:
    """タスクの識別子から編集画面の遷移先を決める。"""
    # 画面識別子に TASK_EDIT_SCREEN_ID を、タスク識別子に受け取った値を入れた遷移先を組み立てて返す
    return EditDestination(screen_id=TASK_EDIT_SCREEN_ID, task_id=task_id)


def to_url(destination: EditDestination) -> str:
    """遷移先を URL 文字列に変換する。"""
    # 画面識別子とタスク識別子を /{画面識別子}/{タスク識別子} の形に組み立てて返す
    return f"/{destination.screen_id}/{destination.task_id}"
