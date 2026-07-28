from __future__ import annotations

import unittest

from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.service import (
    CONTENT_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
    _validate_content,
    _validate_title,
    update_task,
)
from src.tasks.types import Task, TaskStore


class UpdateTaskTest(unittest.TestCase):
    """update_task の単体テスト。"""

    def test_update_task(self) -> None:
        """タイトル・本文を更新する(正常系)。"""
        # 準備
        store: TaskStore = {
            "t1": Task(id="t1", title="買い物リストの作成"),
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        t1_snapshot = store["t1"]

        # 実行
        result = update_task(
            store, "t2", "週次レポートの提出（改訂）", "今週の進捗と来週の予定をまとめる"
        )

        # 検証: 更新後のタスクが返り保管先にも反映される。識別子は変わらず、t1 は変化しない
        self.assertEqual(result.id, "t2")
        self.assertEqual(result.title, "週次レポートの提出（改訂）")
        self.assertEqual(result.content, "今週の進捗と来週の予定をまとめる")
        self.assertEqual(store["t2"], result)
        self.assertEqual(store["t1"], t1_snapshot)

    def test_update_task_when_content_empty(self) -> None:
        """本文を空文字で更新する(正常系)。"""
        # 準備
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }

        # 実行
        result = update_task(store, "t2", "週次レポートの提出", "")

        # 検証: 本文が空文字になり、タイトルは変化しない
        self.assertEqual(result.content, "")
        self.assertEqual(store["t2"].content, "")
        self.assertEqual(store["t2"].title, "週次レポートの提出")

    def test_update_task_when_id_unregistered(self) -> None:
        """未登録の識別子を指定すると TaskNotFoundError を送出する(異常系)。"""
        # 準備
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}
        store_snapshot = dict(store)

        # 実行・検証: 保管先が変化していない
        with self.assertRaises(TaskNotFoundError):
            update_task(store, "t9", "有効なタイトル", "有効な本文")
        self.assertEqual(store, store_snapshot)

    def test_update_task_when_title_empty(self) -> None:
        """タイトルが空文字だと ValidationError を送出する(異常系)。"""
        # 準備
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行・検証: 保管先が変化していない
        with self.assertRaises(ValidationError):
            update_task(store, "t2", "", "変更後の本文")
        self.assertEqual(store, store_snapshot)

    def test_update_task_when_content_over_max_length(self) -> None:
        """本文が上限超過だと ValidationError を送出する(異常系)。"""
        # 準備
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行・検証: 保管先が変化していない
        with self.assertRaises(ValidationError):
            update_task(store, "t2", "有効なタイトル", "a" * (CONTENT_MAX_LENGTH + 1))
        self.assertEqual(store, store_snapshot)

    def test_update_task_when_id_empty(self) -> None:
        """識別子が空文字だと ValidationError を送出する(異常系)。"""
        # 準備
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行・検証: 保管先が変化していない
        with self.assertRaises(ValidationError):
            update_task(store, "", "有効なタイトル", "有効な本文")
        self.assertEqual(store, store_snapshot)


class ValidateTitleTest(unittest.TestCase):
    """_validate_title の単体テスト。"""

    def test_validate_title_when_min_length(self) -> None:
        """下限ちょうどのタイトルは例外を送出しない(正常系)。"""
        # 実行・検証
        _validate_title("t" * TITLE_MIN_LENGTH)

    def test_validate_title_when_max_length(self) -> None:
        """上限ちょうどのタイトルは例外を送出しない(正常系)。"""
        # 実行・検証
        _validate_title("t" * TITLE_MAX_LENGTH)

    def test_validate_title_when_empty(self) -> None:
        """下限未満のタイトルは判定条件と一致したメッセージで ValidationError を送出する(異常系)。"""
        # 実行・検証
        with self.assertRaises(ValidationError) as ctx:
            _validate_title("")
        self.assertIn(str(TITLE_MIN_LENGTH), str(ctx.exception))
        self.assertIn(str(TITLE_MAX_LENGTH), str(ctx.exception))

    def test_validate_title_when_over_max_length(self) -> None:
        """上限超過のタイトルは判定条件と一致したメッセージで ValidationError を送出する(異常系)。"""
        # 実行・検証
        with self.assertRaises(ValidationError) as ctx:
            _validate_title("t" * (TITLE_MAX_LENGTH + 1))
        self.assertIn(str(TITLE_MIN_LENGTH), str(ctx.exception))
        self.assertIn(str(TITLE_MAX_LENGTH), str(ctx.exception))


class ValidateContentTest(unittest.TestCase):
    """_validate_content の単体テスト。"""

    def test_validate_content_when_empty(self) -> None:
        """本文に下限は設けないため、空文字は例外を送出しない(正常系)。"""
        # 実行・検証
        _validate_content("")

    def test_validate_content_when_max_length(self) -> None:
        """上限ちょうどの本文は例外を送出しない(正常系)。"""
        # 実行・検証
        _validate_content("c" * CONTENT_MAX_LENGTH)

    def test_validate_content_when_over_max_length(self) -> None:
        """上限超過の本文は判定条件と一致したメッセージで ValidationError を送出する(異常系)。"""
        # 実行・検証
        with self.assertRaises(ValidationError) as ctx:
            _validate_content("c" * (CONTENT_MAX_LENGTH + 1))
        self.assertIn(str(CONTENT_MAX_LENGTH), str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
