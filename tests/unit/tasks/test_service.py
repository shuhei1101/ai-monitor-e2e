"""`src/tasks/service.py` の単体テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.errors import ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import update_task  # noqa: E402


class UpdateTaskTest(unittest.TestCase):
    def test_update_task(self):
        """タイトルと本文を更新する（正常系）。"""
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        result = update_task(store, "t1", "新タイトル", "新本文")
        self.assertEqual(result.title, "新タイトル")

    def test_update_task_when_title_empty(self):
        """タイトルが空なら ValidationError（異常系）。"""
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "")

    def test_update_task_when_title_too_long(self):
        """タイトルが 101 文字なら ValidationError（異常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "あ" * 101)

    def test_update_task_when_title_max_length(self):
        """タイトルが 100 文字ちょうどなら更新できる（正常系）。"""
        # 準備
        store = {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}
        # 実行
        result = update_task(store, "t1", "あ" * 100)
        # 検証
        self.assertEqual(result.title, "あ" * 100)


if __name__ == "__main__":
    unittest.main()
