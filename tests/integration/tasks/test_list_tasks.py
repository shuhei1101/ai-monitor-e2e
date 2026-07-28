from __future__ import annotations

import unittest

from src.tasks.query import list_tasks
from src.tasks.types import Task, TaskStore


class ListTasksTest(unittest.TestCase):
    """タスク一覧取得の結合テスト。"""

    def test_normal(self) -> None:
        """登録順と識別子の昇順が食い違っても、識別子の昇順で全件返る(正常系)。"""
        # 準備: 登録順を昇順とは逆にして仕込む
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
            "t1": Task(id="t1", title="買い物リストの作成"),
        }
        store_snapshot = dict(store)

        # 実行
        result = list_tasks(store)

        # 検証: t1, t2 の順で 2 件返り、各要素が識別子・タイトル・本文を持ち、保管先の内容が変化していない
        self.assertEqual([task.id for task in result], ["t1", "t2"])
        self.assertEqual(result[0].title, "買い物リストの作成")
        self.assertEqual(result[1].title, "週次レポートの提出")
        self.assertEqual(result[1].content, "今週の進捗をまとめる")
        self.assertEqual(store, store_snapshot)

    def test_normal_when_empty(self) -> None:
        """登録が 0 件のとき空の配列を返す(正常系)。"""
        # 準備
        store: TaskStore = {}

        # 実行
        result = list_tasks(store)

        # 検証
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
