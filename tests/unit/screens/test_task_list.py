from __future__ import annotations

import unittest
from functools import partial

from src.screens.task_list import (
    EMPTY_MESSAGE,
    NOT_FOUND_MESSAGE,
    _build_view,
    render_task_list,
    select_task_row,
)
from src.screens.types import EditNavigation, TaskListView, TaskRow
from src.tasks.query import get_task, list_tasks
from src.tasks.types import Task, TaskStore


class BuildViewTest(unittest.TestCase):
    """_build_view の単体テスト。"""

    def test_build_view(self) -> None:
        """タスクを識別子・タイトルだけの行に移し、渡した順のまま表示状態を組み立てる(正常系)。"""
        # 準備
        tasks = [
            Task(id="t1", title="買い物リストの作成"),
            Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        ]

        # 実行
        result = _build_view(tasks, not_found_message=None)

        # 検証: 2 行の表示状態を返し、渡した順のまま、空状態メッセージが出ない
        self.assertEqual(
            result.rows,
            [
                TaskRow(id="t1", title="買い物リストの作成"),
                TaskRow(id="t2", title="週次レポートの提出"),
            ],
        )
        self.assertIsNone(result.empty_message)

    def test_build_view_when_tasks_empty(self) -> None:
        """タスクが 0 件のとき、行を出さず空状態メッセージを持つ表示状態を返す(正常系)。"""
        # 実行
        result = _build_view([], not_found_message=None)

        # 検証
        self.assertEqual(result.rows, [])
        self.assertEqual(result.empty_message, EMPTY_MESSAGE)

    def test_build_view_when_not_found_message_given(self) -> None:
        """受け取った未検出メッセージをそのまま表示状態へ引き継ぐ(正常系)。"""
        # 実行
        result = _build_view([], not_found_message=NOT_FOUND_MESSAGE)

        # 検証
        self.assertEqual(result.not_found_message, NOT_FOUND_MESSAGE)


class RenderTaskListTest(unittest.TestCase):
    """render_task_list の単体テスト。"""

    def test_render_task_list(self) -> None:
        """一覧取得の結果を表示状態にし、一覧取得が 1 回呼ばれる(正常系)。"""
        # 準備: 呼び出し回数を数えるため一覧取得をラップする
        store: TaskStore = {
            "t1": Task(id="t1", title="買い物リストの作成"),
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        call_count = 0

        def counting_list_tasks() -> list[Task]:
            nonlocal call_count
            call_count += 1
            return list_tasks(store)

        # 実行
        result = render_task_list(list_tasks=counting_list_tasks)

        # 検証: 2 行の表示状態を返し、一覧取得が 1 回呼ばれる
        self.assertEqual([row.id for row in result.rows], ["t1", "t2"])
        self.assertEqual(call_count, 1)


class SelectTaskRowTest(unittest.TestCase):
    """select_task_row の単体テスト。"""

    def test_select_task_row(self) -> None:
        """詳細取得に成功すると、一覧取得を呼ばずに編集画面遷移を返す(正常系)。"""
        # 準備
        store: TaskStore = {
            "t2": Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        }
        list_tasks_calls = 0

        def counting_list_tasks() -> list[Task]:
            nonlocal list_tasks_calls
            list_tasks_calls += 1
            return list_tasks(store)

        # 実行
        result = select_task_row(
            "t2",
            get_task=partial(get_task, store),
            list_tasks=counting_list_tasks,
        )

        # 検証: 編集画面遷移を返し、URL に識別子が含まれ、初期表示値が登録値と一致し、一覧取得が呼ばれない
        self.assertIsInstance(result, EditNavigation)
        assert isinstance(result, EditNavigation)
        self.assertEqual(result.url, "/task-edit/t2")
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "今週の進捗をまとめる")
        self.assertEqual(list_tasks_calls, 0)

    def test_select_task_row_when_task_not_found(self) -> None:
        """対象タスクが見つからないと、一覧を取得し直した未検出メッセージ付きの表示状態を返す(異常系)。"""
        # 準備: 一覧表示後に対象が削除された状態を再現する
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}

        # 実行
        result = select_task_row(
            "t9",
            get_task=partial(get_task, store),
            list_tasks=partial(list_tasks, store),
        )

        # 検証: 未検出メッセージ付きの表示状態を返し、残っているタスクで再表示される
        self.assertIsInstance(result, TaskListView)
        assert isinstance(result, TaskListView)
        self.assertEqual(result.not_found_message, NOT_FOUND_MESSAGE)
        self.assertEqual([row.id for row in result.rows], ["t1"])

    def test_select_task_row_when_task_id_invalid(self) -> None:
        """識別子の形式が不正だと、見つからない場合と同じ未検出メッセージ付きの表示状態を返す(異常系)。"""
        # 準備
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}

        # 実行
        result = select_task_row(
            "",
            get_task=partial(get_task, store),
            list_tasks=partial(list_tasks, store),
        )

        # 検証
        self.assertIsInstance(result, TaskListView)
        assert isinstance(result, TaskListView)
        self.assertEqual(result.not_found_message, NOT_FOUND_MESSAGE)


if __name__ == "__main__":
    unittest.main()
