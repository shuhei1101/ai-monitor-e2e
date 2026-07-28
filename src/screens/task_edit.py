from __future__ import annotations

from src.screens.navigation import TASK_LIST_SCREEN_ID
from src.screens.types import CancelResult, ListNavigation, TaskEditView

# 破棄確認の文言
DISCARD_CONFIRM_MESSAGE: str = "編集内容を破棄してタスク一覧へ戻りますか？"


def render_task_edit(task_id: str, title: str, content: str) -> TaskEditView:
    """引き渡された初期表示値からタスク編集画面の表示状態を作る。"""
    # 受け取ったタイトル・本文を初期表示値と現在の入力値の両方に入れた表示状態を組み立てて返す
    return TaskEditView(
        task_id=task_id,
        initial_title=title,
        initial_content=content,
        title=title,
        content=content,
        confirm_message=None,
    )


def apply_input(
    view: TaskEditView, *, title: str | None = None, content: str | None = None
) -> TaskEditView:
    """入力欄の書き換えを表示状態へ反映する。"""
    # 反映後のタイトルを決める
    if title is not None:
        # タイトルが渡された場合、その値を使う
        next_title = title
    else:
        # タイトルが渡されなかった場合、現在の値を保つ
        next_title = view.title
    # 反映後の本文を決める
    if content is not None:
        # 本文が渡された場合、その値を使う
        next_content = content
    else:
        # 本文が渡されなかった場合、現在の値を保つ
        next_content = view.content
    # 初期表示値と破棄確認メッセージはそのままに、タイトル・本文だけを差し替えた表示状態を返す
    return TaskEditView(
        task_id=view.task_id,
        initial_title=view.initial_title,
        initial_content=view.initial_content,
        title=next_title,
        content=next_content,
        confirm_message=view.confirm_message,
    )


def _has_changes(view: TaskEditView) -> bool:
    """初期表示値と現在の入力値を比較して、変更があるかを返す。"""
    # タイトルと本文をそれぞれ初期表示値と文字列として比較し、いずれかが異なれば True を返す
    return view.title != view.initial_title or view.content != view.initial_content


def cancel_edit(view: TaskEditView) -> CancelResult:
    """中止ボタンの押下を処理し、破棄確認の表示か一覧画面への遷移を返す。"""
    # 変更の有無を判定する
    if _has_changes(view):
        # 変更ありの場合、破棄確認メッセージに DISCARD_CONFIRM_MESSAGE を入れた表示状態を返す
        return TaskEditView(
            task_id=view.task_id,
            initial_title=view.initial_title,
            initial_content=view.initial_content,
            title=view.title,
            content=view.content,
            confirm_message=DISCARD_CONFIRM_MESSAGE,
        )
    else:
        # 変更なしの場合、入力を破棄して一覧画面への遷移先を返す
        return discard_edit(view)


def discard_edit(view: TaskEditView) -> ListNavigation:
    """入力内容を破棄して、一覧画面への遷移先を返す。"""
    # 表示状態の値を引き継がず、画面識別子だけを持つ一覧画面への遷移先を返す
    return ListNavigation(screen_id=TASK_LIST_SCREEN_ID)


def continue_edit(view: TaskEditView) -> TaskEditView:
    """破棄確認を閉じて、入力内容を保持したまま編集画面に留まる。"""
    # 破棄確認メッセージだけを None に差し替えた表示状態を返す
    return TaskEditView(
        task_id=view.task_id,
        initial_title=view.initial_title,
        initial_content=view.initial_content,
        title=view.title,
        content=view.content,
        confirm_message=None,
    )
