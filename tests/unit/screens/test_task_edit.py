from __future__ import annotations

import unittest

from src.screens.task_edit import (
    _has_changes,
    apply_input,
    cancel_edit,
    continue_edit,
    discard_edit,
    render_task_edit,
)
from src.screens.types import ListNavigation, TaskEditView


class RenderTaskEditTest(unittest.TestCase):
    """render_task_edit の単体テスト。"""

    def test_render_task_edit(self) -> None:
        """引き渡された値で表示状態を作る(正常系)。"""
        # 実行
        result = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 検証: 初期表示値と現在の入力値が同じ値になり、confirm_message が None
        self.assertEqual(result.initial_title, "週次レポートの提出")
        self.assertEqual(result.initial_content, "今週の進捗をまとめる")
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "今週の進捗をまとめる")
        self.assertIsNone(result.confirm_message)


class ApplyInputTest(unittest.TestCase):
    """apply_input の単体テスト。"""

    def test_apply_input(self) -> None:
        """タイトルと本文の両方を反映する(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行
        result = apply_input(
            view, title="週次レポートの提出（改訂）", content="来週の予定もまとめる"
        )

        # 検証: タイトル・本文が渡した値になり、初期表示値が変わらない
        self.assertEqual(result.title, "週次レポートの提出（改訂）")
        self.assertEqual(result.content, "来週の予定もまとめる")
        self.assertEqual(result.initial_title, "週次レポートの提出")
        self.assertEqual(result.initial_content, "今週の進捗をまとめる")

    def test_apply_input_when_title_omitted(self) -> None:
        """タイトルを省略する(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行
        result = apply_input(view, content="来週の予定もまとめる")

        # 検証: タイトルが元の値のまま、本文だけ変わる
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "来週の予定もまとめる")

    def test_apply_input_when_content_omitted(self) -> None:
        """本文を省略する(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行
        result = apply_input(view, title="週次レポートの提出（改訂）")

        # 検証: 本文が元の値のまま、タイトルだけ変わる
        self.assertEqual(result.title, "週次レポートの提出（改訂）")
        self.assertEqual(result.content, "今週の進捗をまとめる")


class HasChangesTest(unittest.TestCase):
    """_has_changes の単体テスト。"""

    def test_has_changes(self) -> None:
        """変更がない(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行
        result = _has_changes(view)

        # 検証
        self.assertFalse(result)

    def test_has_changes_when_title_differs(self) -> None:
        """タイトルだけ違う(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )
        view = apply_input(view, title="週次レポートの提出（改訂）")

        # 実行
        result = _has_changes(view)

        # 検証
        self.assertTrue(result)

    def test_has_changes_when_content_differs(self) -> None:
        """本文だけ違う(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )
        view = apply_input(view, content="来週の予定もまとめる")

        # 実行
        result = _has_changes(view)

        # 検証
        self.assertTrue(result)

    def test_has_changes_when_only_whitespace_differs(self) -> None:
        """前後の空白だけ違う(正常系)。"""
        # 準備: タイトルの末尾に空白を足した表示状態
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )
        view = apply_input(view, title="週次レポートの提出 ")

        # 実行
        result = _has_changes(view)

        # 検証: 前後の空白を正規化せず、変更ありと判定する
        self.assertTrue(result)


class CancelEditTest(unittest.TestCase):
    """cancel_edit の単体テスト。"""

    def test_cancel_edit(self) -> None:
        """変更ありで確認を出す(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )
        view = apply_input(view, title="週次レポートの提出（改訂）")

        # 実行
        result = cancel_edit(view)

        # 検証: TaskEditView を返し、confirm_message に破棄確認の文言が入り、タイトル・本文が保持される
        self.assertIsInstance(result, TaskEditView)
        assert isinstance(result, TaskEditView)
        self.assertEqual(result.confirm_message, "編集内容を破棄してタスク一覧へ戻りますか？")
        self.assertEqual(result.title, "週次レポートの提出（改訂）")
        self.assertEqual(result.content, "今週の進捗をまとめる")

    def test_cancel_edit_when_no_changes(self) -> None:
        """変更なしで遷移する(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )

        # 実行
        result = cancel_edit(view)

        # 検証: ListNavigation を返し、screen_id が task-list
        self.assertIsInstance(result, ListNavigation)
        assert isinstance(result, ListNavigation)
        self.assertEqual(result.screen_id, "task-list")


class DiscardEditTest(unittest.TestCase):
    """discard_edit の単体テスト。"""

    def test_discard_edit(self) -> None:
        """一覧画面への遷移先を返す(正常系)。"""
        # 準備
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )
        view = apply_input(view, title="週次レポートの提出（改訂）")

        # 実行
        result = discard_edit(view)

        # 検証: screen_id が task-list の遷移先を返す
        self.assertEqual(result, ListNavigation(screen_id="task-list"))


class ContinueEditTest(unittest.TestCase):
    """continue_edit の単体テスト。"""

    def test_continue_edit(self) -> None:
        """確認を閉じて入力を保持する(正常系)。"""
        # 準備: 破棄確認メッセージ付きの表示状態
        view = render_task_edit(
            task_id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"
        )
        view = apply_input(view, title="週次レポートの提出（改訂）")
        confirmed = cancel_edit(view)
        assert isinstance(confirmed, TaskEditView)

        # 実行
        result = continue_edit(confirmed)

        # 検証: confirm_message が None になり、タイトル・本文が変わらない
        self.assertIsNone(result.confirm_message)
        self.assertEqual(result.title, "週次レポートの提出（改訂）")
        self.assertEqual(result.content, "今週の進捗をまとめる")


if __name__ == "__main__":
    unittest.main()
