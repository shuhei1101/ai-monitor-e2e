from __future__ import annotations

import unittest
from dataclasses import fields
from functools import partial

from src.screens.navigation import TASK_EDIT_SCREEN_ID
from src.screens.task_list import render_task_list, select_task_row
from src.screens.types import EditNavigation, GetTask, ListTasks, TaskListView, TaskRow
from src.tasks.query import get_task, list_tasks
from src.tasks.types import Task, TaskStore


def _wire_screen(store: TaskStore) -> tuple[ListTasks, GetTask]:
    """保管先をタスク一覧画面が使う一覧取得・詳細取得へ配線する。"""
    # 保管先を束ねる composition root が未作成のため、配線をテスト側で作る
    return partial(list_tasks, store), partial(get_task, store)


class TaskListToEditNavigationTest(unittest.TestCase):
    """タスク一覧画面から編集画面への遷移導線の追加の E2E テスト。"""

    def test_normal_when_selecting_row_from_task_list(self) -> None:
        """一覧のタスク行を選ぶと、その行のタスクの編集画面へ初期表示値付きで遷移する(正常系)。"""
        # 準備: タスクを 2 件登録した状態で一覧画面を配線する
        store: TaskStore = {
            "t1": Task(id="t1", title="買い物リストの作成"),
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        store_snapshot = dict(store)
        list_tasks_fn, get_task_fn = _wire_screen(store)

        # 実行: タスク一覧画面を開き、2 件目のタスク行を選ぶ
        view = render_task_list(list_tasks=list_tasks_fn)
        result = select_task_row(
            view.rows[1].id, get_task=get_task_fn, list_tasks=list_tasks_fn
        )

        # 検証: タスク行が 2 件表示され、遷移先が編集画面で URL に 2 件目の識別子が含まれ、
        # 初期表示値が 2 件目の登録値と一致し、保管されているタスクの内容が変化していない
        self.assertEqual([row.id for row in view.rows], ["t1", "t2"])
        self.assertIsInstance(result, EditNavigation)
        assert isinstance(result, EditNavigation)
        self.assertEqual(result.destination.screen_id, TASK_EDIT_SCREEN_ID)
        self.assertEqual(result.destination.task_id, "t2")
        self.assertIn("t2", result.url)
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "今週の進捗をまとめる")
        self.assertEqual(store, store_snapshot)

        # 検証: 1 件目の行を選んだ場合も同じ流れで 1 件目の編集画面へ遷移する
        first_result = select_task_row(
            view.rows[0].id, get_task=get_task_fn, list_tasks=list_tasks_fn
        )
        self.assertIsInstance(first_result, EditNavigation)
        assert isinstance(first_result, EditNavigation)
        self.assertEqual(first_result.destination.task_id, "t1")
        self.assertEqual(first_result.title, "買い物リストの作成")

    def test_normal_when_returning_to_task_list(self) -> None:
        """編集画面へ遷移した後に一覧を表示し直すと、遷移前と同じ内容の一覧になる(正常系)。"""
        # 準備: タスクを 1 件登録し、一覧のタスク行から編集画面へ遷移済みの状態を作る
        store: TaskStore = {"t1": Task(id="t1", title="週次レポートの提出")}
        store_snapshot = dict(store)
        list_tasks_fn, get_task_fn = _wire_screen(store)
        view_before = render_task_list(list_tasks=list_tasks_fn)
        navigation = select_task_row(
            view_before.rows[0].id, get_task=get_task_fn, list_tasks=list_tasks_fn
        )
        self.assertIsInstance(navigation, EditNavigation)

        # 実行: 一覧へ戻る(一覧を表示し直す)
        view_after = render_task_list(list_tasks=list_tasks_fn)

        # 検証: タスク一覧画面が表示され、対象タスクの行が遷移前と同じ内容で並び、
        # 保管されているタスクの内容が変化していない
        self.assertEqual(view_after.rows, view_before.rows)
        self.assertIsNone(view_after.empty_message)
        self.assertIsNone(view_after.not_found_message)
        self.assertEqual(store, store_snapshot)

    def test_normal_when_layout_unchanged(self) -> None:
        """導線を追加した後もタスク行の表示項目が増えず、行自体が選択の対象になっている(正常系)。"""
        # 準備: タスクを 1 件登録した状態で一覧画面を配線する
        store: TaskStore = {"t1": Task(id="t1", title="週次レポートの提出")}
        list_tasks_fn, get_task_fn = _wire_screen(store)

        # 実行: タスク一覧画面を開き、表示されたタスク行を選ぶ
        view = render_task_list(list_tasks=list_tasks_fn)
        result = select_task_row(
            view.rows[0].id, get_task=get_task_fn, list_tasks=list_tasks_fn
        )

        # 検証: タスク行の表示項目が識別子・タイトルだけで編集ボタン等の要素が増えておらず、
        # 行が持つ識別子だけで編集画面への遷移が決まっている
        self.assertEqual([field.name for field in fields(TaskRow)], ["id", "title"])
        self.assertIsInstance(result, EditNavigation)

    def test_error_when_task_deleted_after_listing(self) -> None:
        """一覧表示後に削除されたタスクの行を選ぶと、遷移せず見つからない旨を表示する(異常系)。"""
        # 準備: タスクを 1 件登録して一覧を表示し、その後に対象タスクを削除する
        store: TaskStore = {"t1": Task(id="t1", title="週次レポートの提出")}
        list_tasks_fn, get_task_fn = _wire_screen(store)
        view = render_task_list(list_tasks=list_tasks_fn)
        target_id = view.rows[0].id
        del store[target_id]

        # 実行: 削除済みタスクの行を選ぶ
        result = select_task_row(
            target_id, get_task=get_task_fn, list_tasks=list_tasks_fn
        )

        # 検証: 編集画面へ遷移せずタスク一覧画面に留まって未検出メッセージが表示され、
        # 保管先に対象タスクが存在しない
        self.assertIsInstance(result, TaskListView)
        assert isinstance(result, TaskListView)
        self.assertEqual(result.not_found_message, "タスクが見つかりません")
        self.assertNotIn(target_id, store)


if __name__ == "__main__":
    unittest.main()
