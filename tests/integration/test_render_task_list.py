from __future__ import annotations

import unittest
from functools import partial

from src.screens.task_list import render_task_list
from src.tasks.query import list_tasks
from src.tasks.types import Task, TaskStore


class RenderTaskListTest(unittest.TestCase):
    """タスク一覧画面の表示の結合テスト。"""

    def test_normal(self) -> None:
        """取得したタスクを識別子の昇順でタスク行として表示する(正常系)。"""
        # 準備
        store: TaskStore = {
            "t1": Task(id="t1", title="買い物リストの作成"),
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }

        # 実行
        result = render_task_list(list_tasks=partial(list_tasks, store))

        # 検証: t1, t2 の順で 2 行表示され、各行に識別子・タイトルが表示され、
        # 空状態メッセージ・未検出メッセージが表示されていない
        self.assertEqual([row.id for row in result.rows], ["t1", "t2"])
        self.assertEqual(result.rows[0].title, "買い物リストの作成")
        self.assertEqual(result.rows[1].title, "週次レポートの提出")
        self.assertIsNone(result.empty_message)
        self.assertIsNone(result.not_found_message)

    def test_normal_when_zero_tasks(self) -> None:
        """登録が 0 件のとき空状態メッセージを表示する(正常系)。"""
        # 準備
        store: TaskStore = {}

        # 実行
        result = render_task_list(list_tasks=partial(list_tasks, store))

        # 検証: 空状態メッセージが表示され、タスク表が表示されず、例外が送出されない
        self.assertEqual(result.rows, [])
        self.assertEqual(result.empty_message, "タスクがありません")

    def test_normal_when_returning_from_edit_screen(self) -> None:
        """編集画面から戻ったとき、一覧を取得し直して最新の内容で表示する(正常系)。"""
        # 準備: 一覧画面から編集画面へ遷移済み(1 回目の取得を済ませた状態)を再現する
        store: TaskStore = {
            "t1": Task(id="t1", title="買い物リストの作成"),
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        call_count = 0

        def counting_list_tasks() -> list[Task]:
            nonlocal call_count
            call_count += 1
            return list_tasks(store)

        render_task_list(list_tasks=counting_list_tasks)
        del store["t2"]

        # 実行: 一覧画面へ戻る
        result = render_task_list(list_tasks=counting_list_tasks)

        # 検証: タスク一覧取得が 2 回目の呼び出しを受け、1 件で表示され、遷移前の取得結果が残っていない
        self.assertEqual(call_count, 2)
        self.assertEqual([row.id for row in result.rows], ["t1"])


if __name__ == "__main__":
    unittest.main()
