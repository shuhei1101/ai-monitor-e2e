from __future__ import annotations

import unittest

from src.screens.task_edit import (
    apply_input,
    cancel_edit,
    continue_edit,
    discard_edit,
    render_task_edit,
)
from src.screens.types import ListNavigation, TaskEditView


class TaskEditCancelTest(unittest.TestCase):
    """タスク編集の中止の結合テスト。"""

    def test_normal(self) -> None:
        """変更ありで中止し、破棄確認の「戻る」で一覧画面へ戻る(正常系)。"""
        # 準備: タイトル・本文を初期表示値として編集画面を表示済みの状態を再現する
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行: タイトルを書き換えたあと中止ボタンを押し、確認ダイアログで戻るを選ぶ
        view = apply_input(view, title="週次レポートの提出（改訂）")
        confirmed = cancel_edit(view)
        assert isinstance(confirmed, TaskEditView)
        result = discard_edit(confirmed)

        # 検証: タスク一覧画面へ遷移している。更新・取得操作は引数に注入点がなく呼び出しようがない
        self.assertEqual(result, ListNavigation(screen_id="task-list"))

    def test_normal_when_no_changes(self) -> None:
        """入力を変更せずに中止し、確認を挟まず一覧画面へ戻る(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行: 入力を変更せずに中止ボタンを押す
        result = cancel_edit(view)

        # 検証: 確認ダイアログを経ずにタスク一覧画面へ遷移している
        self.assertEqual(result, ListNavigation(screen_id="task-list"))

    def test_normal_when_continue_edit(self) -> None:
        """破棄確認で編集を続けると、ダイアログを閉じて編集画面に留まる(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行: 本文を書き換えたあと中止ボタンを押し、確認ダイアログで編集を続けるを選ぶ
        view = apply_input(view, content="来週の予定もまとめる")
        confirmed = cancel_edit(view)
        assert isinstance(confirmed, TaskEditView)
        result = continue_edit(confirmed)

        # 検証: 編集画面に留まり、書き換えた本文が保持され、タイトルは初期表示値のまま、確認ダイアログが表示されていない
        self.assertEqual(result.content, "来週の予定もまとめる")
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertIsNone(result.confirm_message)

    def test_normal_when_reopened_after_cancel(self) -> None:
        """中止したあとに同じタスクの編集画面を開き直すと、保管済みの値が初期表示される(正常系)。"""
        # 準備: タイトルを書き換えたあと編集の中止でタスク一覧画面へ戻った直後の状態を再現する
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )
        view = apply_input(view, title="週次レポートの提出（改訂）")
        confirmed = cancel_edit(view)
        assert isinstance(confirmed, TaskEditView)
        discard_edit(confirmed)

        # 実行: 保管済みの値を初期表示値として同じタスクの編集画面をもう一度開く
        result = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 検証: タイトル・本文が保管済みの値で表示され、破棄確認ダイアログが表示されていない
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "今週の進捗をまとめる")
        self.assertIsNone(result.confirm_message)


if __name__ == "__main__":
    unittest.main()
