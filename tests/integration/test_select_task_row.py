from __future__ import annotations

import unittest
from functools import partial

from src.screens.navigation import TASK_EDIT_SCREEN_ID
from src.screens.task_list import select_task_row
from src.screens.types import EditNavigation, TaskListView
from src.tasks.query import get_task, list_tasks
from src.tasks.types import Task, TaskStore


class SelectTaskRowTest(unittest.TestCase):
    """編集画面への遷移の結合テスト。"""

    def test_normal(self) -> None:
        """選択した行のタスクの詳細を取得し、編集画面へ遷移する(正常系)。"""
        # 準備: 一覧の 2 件目(t2)を選んだ状態を再現する
        store: TaskStore = {
            "t1": Task(id="t1", title="買い物リストの作成"),
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)

        # 実行
        result = select_task_row(
            "t2",
            get_task=partial(get_task, store),
            list_tasks=partial(list_tasks, store),
        )

        # 検証: 遷移先が編集画面で URL に識別子 t2 が含まれ、初期表示値が t2 の登録値と一致し、
        # 未検出メッセージが表示されず、保管されているタスクの内容が変化していない
        self.assertIsInstance(result, EditNavigation)
        assert isinstance(result, EditNavigation)
        self.assertEqual(result.destination.screen_id, TASK_EDIT_SCREEN_ID)
        self.assertIn("t2", result.url)
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "今週の進捗をまとめる")
        self.assertEqual(store, store_snapshot)

    def test_error_when_task_not_found(self) -> None:
        """対象タスクが見つからないと遷移せず未検出メッセージを表示し、一覧を取得し直す(異常系)。"""
        # 準備: 一覧表示後に対象(t2)が削除された状態を再現する
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}
        store_snapshot = dict(store)

        # 実行: 削除済みの t2 の行を選択する
        result = select_task_row(
            "t2",
            get_task=partial(get_task, store),
            list_tasks=partial(list_tasks, store),
        )

        # 検証: 編集画面へ遷移しておらずタスク一覧画面に留まり、未検出メッセージが表示され、
        # タスク行が取得し直した内容(1 件)で表示され、保管されているタスクの内容が変化していない
        self.assertIsInstance(result, TaskListView)
        assert isinstance(result, TaskListView)
        self.assertEqual(result.not_found_message, "タスクが見つかりません")
        self.assertEqual([row.id for row in result.rows], ["t1"])
        self.assertEqual(store, store_snapshot)

    def test_error_when_task_id_invalid(self) -> None:
        """識別子の形式が不正だと見つからない場合と同じ表示になり、未捕捉の内部エラーにならない(異常系)。"""
        # 準備: 識別子が空文字のタスク行が 1 件表示されている状態を再現する(一覧由来では起こらない値)
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}
        store_snapshot = dict(store)

        # 実行: 識別子が空文字の行を選択する
        result = select_task_row(
            "",
            get_task=partial(get_task, store),
            list_tasks=partial(list_tasks, store),
        )

        # 検証: 編集画面へ遷移しておらず、見つからない場合と同じ未検出メッセージが表示され、
        # 保管されているタスクの内容が変化していない
        self.assertIsInstance(result, TaskListView)
        assert isinstance(result, TaskListView)
        self.assertEqual(result.not_found_message, "タスクが見つかりません")
        self.assertEqual(store, store_snapshot)


if __name__ == "__main__":
    unittest.main()
