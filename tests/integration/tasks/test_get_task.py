from __future__ import annotations

import unittest

from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.query import TASK_ID_MAX_LENGTH, TASK_ID_MIN_LENGTH, get_task
from src.tasks.types import Task, TaskStore


class GetTaskTest(unittest.TestCase):
    """タスク詳細取得の結合テスト。"""

    def test_normal(self) -> None:
        """登録済みの識別子でタスク 1 件を返す(正常系)。"""
        # 準備: 一覧の 2 件目を選んだ状態を再現する
        store: TaskStore = {
            "t1": Task(id="t1", title="買い物リストの作成"),
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行
        result = get_task(store, "t2")

        # 検証: タイトル・本文が登録値と一致し、保管先の内容が変化していない
        self.assertEqual(result.id, "t2")
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "今週の進捗をまとめる")
        self.assertEqual(store, store_snapshot)

    def test_error_when_not_found(self) -> None:
        """一覧表示後に削除されたタスクの行をクリックした場合に相当する、未登録の識別子を指定するとタスクが見つからない例外を送出する(異常系)。"""
        # 準備: 一覧表示後に対象が削除された状態を再現する
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}
        store_snapshot = dict(store)

        # 実行・検証
        with self.assertRaises(TaskNotFoundError):
            get_task(store, "t9")
        self.assertEqual(store, store_snapshot)

    def test_error_when_invalid_format(self) -> None:
        """空文字の識別子を指定すると、未捕捉の内部エラーにはならず入力不正の例外を送出する(異常系)。"""
        # 準備: 形式検証の下限違反を決定的に誘発する
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}
        store_snapshot = dict(store)

        # 実行・検証: 例外メッセージが判定条件と一致している
        with self.assertRaises(ValidationError) as ctx:
            get_task(store, "")
        self.assertIn(str(TASK_ID_MIN_LENGTH), str(ctx.exception))
        self.assertIn(str(TASK_ID_MAX_LENGTH), str(ctx.exception))
        self.assertEqual(store, store_snapshot)


if __name__ == "__main__":
    unittest.main()
