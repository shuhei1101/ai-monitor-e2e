"""`src/tasks/service.py` の単体テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tasks.errors import TaskNotFoundError, ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import update_task  # noqa: E402


def _store() -> dict[str, Task]:
    return {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}


class UpdateTaskTest(unittest.TestCase):
    def test_update_task(self):
        """タイトルと本文を更新する（正常系）。"""
        # 準備
        store = _store()
        # 実行
        result = update_task(store, "t1", "新タイトル", "新本文")
        # 検証
        self.assertEqual(result.title, "新タイトル")
        self.assertEqual(result.content, "新本文")
        self.assertEqual(store["t1"].title, "新タイトル")

    def test_update_task_when_content_omitted(self):
        """本文を省略すると空文字になる（正常系）。"""
        # 準備
        store = _store()
        # 実行
        result = update_task(store, "t1", "新タイトル")
        # 検証
        self.assertEqual(result.content, "")

    def test_update_task_when_title_empty(self):
        """タイトルが空なら ValidationError（異常系）。"""
        # 準備
        store = _store()
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "")

    def test_update_task_when_title_too_long(self):
        """タイトルが 101 文字なら ValidationError（異常系）。"""
        # 準備
        store = _store()
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "a" * 101)

    def test_update_task_when_content_too_long(self):
        """本文が 1001 文字なら ValidationError（異常系）。"""
        # 準備
        store = _store()
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "新タイトル", "a" * 1001)

    def test_update_task_when_task_missing(self):
        """未登録の task_id なら TaskNotFoundError（異常系）。"""
        # 準備
        store = _store()
        # 実行・検証
        with self.assertRaises(TaskNotFoundError):
            update_task(store, "missing", "新タイトル")
        self.assertEqual(store["t1"].title, "旧タイトル")


if __name__ == "__main__":
    unittest.main()
