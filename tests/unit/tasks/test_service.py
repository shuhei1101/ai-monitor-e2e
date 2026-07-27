"""tasks.service (update_task) の単体テスト。"""
from __future__ import annotations

import unittest

from tasks.errors import TaskNotFoundError, ValidationError
from tasks.models import Task
from tasks.service import update_task


class UpdateTaskTest(unittest.TestCase):
    """update_task の単体テスト。"""

    def setUp(self) -> None:
        # 準備: t1 を登録済みのストアを用意する
        self.store = {"t1": Task(id="t1", title="買い物", content="牛乳")}

    def test_update_task(self) -> None:
        """タイトルと本文を更新して返し、ストアも更新される（正常系）。"""
        # 実行
        result = update_task(self.store, "t1", "掃除", "部屋の掃除")
        # 検証
        self.assertEqual(result, Task(id="t1", title="掃除", content="部屋の掃除"))
        self.assertEqual(self.store["t1"], Task(id="t1", title="掃除", content="部屋の掃除"))

    def test_update_task_when_content_omitted(self) -> None:
        """content を渡さないと本文が空文字になる（正常系）。"""
        # 実行
        result = update_task(self.store, "t1", "掃除")
        # 検証
        self.assertEqual(result.content, "")

    def test_update_task_when_title_empty(self) -> None:
        """title が空文字だと ValidationError になる（異常系）。"""
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(self.store, "t1", "")

    def test_update_task_when_title_too_long(self) -> None:
        """title が 101 文字だと ValidationError になる（異常系）。"""
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(self.store, "t1", "あ" * 101)

    def test_update_task_when_content_too_long(self) -> None:
        """content が 1001 文字だと ValidationError になる（異常系）。"""
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(self.store, "t1", "掃除", "あ" * 1001)

    def test_update_task_when_task_missing(self) -> None:
        """未登録の task_id を指定すると TaskNotFoundError になり、ストアは不変（異常系）。"""
        # 準備
        before = dict(self.store)
        # 実行・検証
        with self.assertRaises(TaskNotFoundError):
            update_task(self.store, "unknown", "掃除")
        self.assertEqual(self.store, before)


if __name__ == "__main__":
    unittest.main()
