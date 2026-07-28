from __future__ import annotations

import unittest

from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.query import TASK_ID_MAX_LENGTH, TASK_ID_MIN_LENGTH
from src.tasks.service import CONTENT_MAX_LENGTH, TITLE_MAX_LENGTH, TITLE_MIN_LENGTH, update_task
from src.tasks.types import Task, TaskStore


class UpdateTaskTest(unittest.TestCase):
    """タスク更新の結合テスト。"""

    def test_normal(self) -> None:
        """編集画面でタイトルと本文の両方を書き換えた状態を再現し、更新後のタスクを返す(正常系)。"""
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

        # 検証: 更新後のタイトル・本文を持つタスクが返り、識別子は変わらず、t1 は変化しない
        self.assertEqual(result.id, "t2")
        self.assertEqual(result.title, "週次レポートの提出（改訂）")
        self.assertEqual(result.content, "今週の進捗と来週の予定をまとめる")
        self.assertEqual(store["t2"], result)
        self.assertEqual(store["t1"], t1_snapshot)

    def test_normal_when_content_empty(self) -> None:
        """本文をすべて削除して保存した状態を再現し、本文が空文字のタスクを返す(正常系)。"""
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

    def test_error_when_title_empty(self) -> None:
        """フロントエンドの必須チェックをすり抜けた場合に相当する、空文字のタイトルを指定すると入力不正の例外を送出する(異常系)。"""
        # 準備: タイトル検証の下限違反を決定的に誘発する
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行・検証: 例外メッセージが判定条件と一致し、保管先が変化していない
        with self.assertRaises(ValidationError) as ctx:
            update_task(store, "t2", "", "今週の進捗と来週の予定をまとめる")
        self.assertIn(str(TITLE_MIN_LENGTH), str(ctx.exception))
        self.assertIn(str(TITLE_MAX_LENGTH), str(ctx.exception))
        self.assertEqual(store, store_snapshot)

    def test_error_when_content_over_max_length(self) -> None:
        """1001 文字の本文を指定すると入力不正の例外を送出する(異常系)。"""
        # 準備: 本文検証の上限違反を決定的に誘発する
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行・検証: 例外メッセージが判定条件と一致し、保管先が変化していない
        with self.assertRaises(ValidationError) as ctx:
            update_task(store, "t2", "有効なタイトル", "a" * (CONTENT_MAX_LENGTH + 1))
        self.assertIn(str(CONTENT_MAX_LENGTH), str(ctx.exception))
        self.assertEqual(store, store_snapshot)

    def test_error_when_invalid_format(self) -> None:
        """空文字の識別子を指定すると入力不正の例外を送出する(異常系)。"""
        # 準備: 識別子検証の下限違反を決定的に誘発する
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行・検証: 例外メッセージが判定条件と一致し、保管先が変化していない
        with self.assertRaises(ValidationError) as ctx:
            update_task(store, "", "有効なタイトル", "有効な本文")
        self.assertIn(str(TASK_ID_MIN_LENGTH), str(ctx.exception))
        self.assertIn(str(TASK_ID_MAX_LENGTH), str(ctx.exception))
        self.assertEqual(store, store_snapshot)

    def test_error_when_not_found(self) -> None:
        """編集画面を開いた後に対象が削除された場合に相当する、未登録の識別子を指定するとタスクが見つからない例外を送出する(異常系)。"""
        # 準備: 編集画面を開いた後に対象が削除された状態を再現する
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}
        store_snapshot = dict(store)

        # 実行・検証: 入力不正の例外とは型で区別でき、保管先に識別子 t9 のタスクが新しく作られない
        with self.assertRaises(TaskNotFoundError) as ctx:
            update_task(store, "t9", "有効なタイトル", "有効な本文")
        self.assertNotIsInstance(ctx.exception, ValidationError)
        self.assertEqual(store, store_snapshot)


if __name__ == "__main__":
    unittest.main()
