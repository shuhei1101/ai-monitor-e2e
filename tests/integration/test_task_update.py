"""PATCH /tasks/{task_id}（タスク更新）の結合テスト。"""
from __future__ import annotations

import unittest

from tasks.errors import TaskNotFoundError, ValidationError
from tasks.models import Task
from tasks.service import update_task


class TaskUpdateIntegrationTest(unittest.TestCase):
    """タスク更新の結合テスト。"""

    def setUp(self) -> None:
        # 準備: t1 を登録済みのストアを用意する
        self.store = {"t1": Task(id="t1", title="買い物", content="牛乳")}

    def test_normal(self) -> None:
        """対象タスクのタイトルと本文を更新して返す（正常系）。"""
        # 実行
        result = update_task(self.store, "t1", "掃除", "部屋の掃除")
        # 検証
        self.assertEqual(result, Task(id="t1", title="掃除", content="部屋の掃除"))
        self.assertEqual(self.store["t1"], Task(id="t1", title="掃除", content="部屋の掃除"))

    def test_error_when_task_not_found(self) -> None:
        """未登録の task_id を指定すると TaskNotFoundError になり、ストアが変更されない（異常系（タスク不明））。"""
        # 準備
        before = dict(self.store)
        # 実行・検証
        with self.assertRaises(TaskNotFoundError):
            update_task(self.store, "unknown", "掃除")
        self.assertEqual(self.store, before)

    def test_error_when_title_empty(self) -> None:
        """title に空文字を指定すると ValidationError になり、ストアが変更されない(異常系（タイトルが空）)。"""
        # 準備
        before = dict(self.store)
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(self.store, "t1", "")
        self.assertEqual(self.store, before)


if __name__ == "__main__":
    unittest.main()
