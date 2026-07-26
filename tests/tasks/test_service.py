"""tasks/service.py の update_task 単体テスト。"""
from __future__ import annotations

import unittest

from tasks.errors import TaskNotFoundError, ValidationError
from tasks.models import Task
from tasks.service import update_task


class UpdateTaskTest(unittest.TestCase):
    """update_task の単体テスト。"""

    def test_update_task(self) -> None:
        """タイトルと本文を更新する（正常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行
        result = update_task(store, "t1", "買い物", "牛乳")
        # 検証
        self.assertEqual(result, Task(id="t1", title="買い物", content="牛乳"))
        self.assertEqual(store["t1"], Task(id="t1", title="買い物", content="牛乳"))

    def test_update_task_when_content_omitted(self) -> None:
        """content を省略すると本文が空文字になる（正常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行
        result = update_task(store, "t1", "買い物")
        # 検証
        self.assertEqual(result.content, "")

    def test_update_task_when_title_empty(self) -> None:
        """title が空文字なら ValidationError（異常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "")
        self.assertEqual(store["t1"], Task(id="t1", title="旧タイトル", content="旧本文"))

    def test_update_task_when_title_too_long(self) -> None:
        """title が 101 文字なら ValidationError（異常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "あ" * 101)
        self.assertEqual(store["t1"], Task(id="t1", title="旧タイトル", content="旧本文"))

    def test_update_task_when_content_too_long(self) -> None:
        """content が 1001 文字なら ValidationError（異常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "買い物", "あ" * 1001)
        self.assertEqual(store["t1"], Task(id="t1", title="旧タイトル", content="旧本文"))

    def test_update_task_when_task_missing(self) -> None:
        """未登録の task_id なら TaskNotFoundError で、ストアは不変（異常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行・検証
        with self.assertRaises(TaskNotFoundError):
            update_task(store, "unknown", "買い物", "牛乳")
        self.assertEqual(store, {"t1": Task(id="t1", title="旧タイトル", content="旧本文")})


if __name__ == "__main__":
    unittest.main()
