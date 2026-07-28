from __future__ import annotations

import unittest

from src.screens.task_list import _build_view, render_task_list, select_task_row
from src.screens.types import EditNavigation, TaskListView, TaskRow
from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.types import Task


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
        self.assertEqual(result.empty_message, "タスクがありません")

    def test_build_view_when_not_found_message_given(self) -> None:
        """受け取った未検出メッセージをそのまま表示状態へ引き継ぐ(正常系)。"""
        # 実行
        result = _build_view([], not_found_message="テスト用メッセージ")

        # 検証
        self.assertEqual(result.not_found_message, "テスト用メッセージ")


class RenderTaskListTest(unittest.TestCase):
    """render_task_list の単体テスト。"""

    def test_render_task_list(self) -> None:
        """一覧取得の結果を表示状態にし、一覧取得が 1 回呼ばれる(正常系)。"""
        # 準備: 固定のタスクを返すだけの Mock 関数を用意し、呼び出し回数を記録する
        tasks = [
            Task(id="t1", title="買い物リストの作成"),
            Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる"),
        ]
        call_count = 0

        def mock_list_tasks() -> list[Task]:
            nonlocal call_count
            call_count += 1
            return tasks

        # 実行
        result = render_task_list(list_tasks=mock_list_tasks)

        # 検証: 2 行の表示状態を返し、一覧取得が 1 回呼ばれる
        self.assertEqual([row.id for row in result.rows], ["t1", "t2"])
        self.assertEqual(call_count, 1)


class SelectTaskRowTest(unittest.TestCase):
    """select_task_row の単体テスト。"""

    def test_select_task_row(self) -> None:
        """詳細取得に成功すると、一覧取得を呼ばずに編集画面遷移を返す(正常系)。"""
        # 準備: 固定のタスクを返すだけの Mock 関数を用意し、渡された識別子を記録する
        task = Task(id="t2", title="週次レポートの提出", content="今週の進捗をまとめる")
        get_task_calls: list[str] = []
        list_tasks_calls = 0

        def mock_get_task(task_id: str) -> Task:
            get_task_calls.append(task_id)
            return task

        def mock_list_tasks() -> list[Task]:
            nonlocal list_tasks_calls
            list_tasks_calls += 1
            return []

        # 実行
        result = select_task_row(
            "t2",
            get_task=mock_get_task,
            list_tasks=mock_list_tasks,
        )

        # 検証: 編集画面遷移を返し、URL に識別子が含まれ、初期表示値が登録値と一致し、
        # 詳細取得に t2 が渡り、一覧取得が呼ばれない
        self.assertIsInstance(result, EditNavigation)
        assert isinstance(result, EditNavigation)
        self.assertEqual(result.url, "/task-edit/t2")
        self.assertEqual(result.title, "週次レポートの提出")
        self.assertEqual(result.content, "今週の進捗をまとめる")
        self.assertEqual(get_task_calls, ["t2"])
        self.assertEqual(list_tasks_calls, 0)

    def test_select_task_row_when_task_not_found(self) -> None:
        """対象タスクが見つからないと、一覧を取得し直した未検出メッセージ付きの表示状態を返す(異常系)。"""
        # 準備: 詳細取得を見つからないエラーを送出する Mock に、一覧取得を残りのタスクを返す Mock にする
        def mock_get_task(task_id: str) -> Task:
            raise TaskNotFoundError(f"タスクが見つかりません: {task_id}")

        def mock_list_tasks() -> list[Task]:
            return [Task(id="t1", title="買い物リストの作成")]

        # 実行
        result = select_task_row(
            "t9",
            get_task=mock_get_task,
            list_tasks=mock_list_tasks,
        )

        # 検証: 未検出メッセージ付きの表示状態を返し、残っているタスクで再表示される
        self.assertIsInstance(result, TaskListView)
        assert isinstance(result, TaskListView)
        self.assertEqual(result.not_found_message, "タスクが見つかりません")
        self.assertEqual([row.id for row in result.rows], ["t1"])

    def test_select_task_row_when_task_id_invalid(self) -> None:
        """識別子の形式が不正だと、見つからない場合と同じ未検出メッセージ付きの表示状態を返す(異常系)。"""
        # 準備: 詳細取得を入力不正エラーを送出する Mock に、一覧取得を残りのタスクを返す Mock にする
        def mock_get_task(task_id: str) -> Task:
            raise ValidationError("task_id は 1 文字以上 100 文字以内")

        def mock_list_tasks() -> list[Task]:
            return [Task(id="t1", title="買い物リストの作成")]

        # 実行
        result = select_task_row(
            "",
            get_task=mock_get_task,
            list_tasks=mock_list_tasks,
        )

        # 検証
        self.assertIsInstance(result, TaskListView)
        assert isinstance(result, TaskListView)
        self.assertEqual(result.not_found_message, "タスクが見つかりません")


if __name__ == "__main__":
    unittest.main()
