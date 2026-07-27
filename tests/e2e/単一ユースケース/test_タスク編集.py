"""単一UC「タスク編集」の E2E テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.errors import ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import update_task  # noqa: E402


def _store() -> dict[str, Task]:
    return {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}


class タスク編集Test(unittest.TestCase):
    def test_normal(self):
        """一覧から選んだタスクを編集して保存する（正常系）。"""
        store = _store()
        update_task(store, "t1", "新タイトル", "新本文")
        self.assertEqual(store["t1"].title, "新タイトル")
        self.assertEqual(store["t1"].content, "新本文")

    def test_normal_when_タイトルが空(self):
        """タイトルを空にして保存すると空タイトルのまま保存される（正常系）。"""
        store = _store()
        update_task(store, "t1", "")
        self.assertEqual(store["t1"].title, "")


if __name__ == "__main__":
    unittest.main()
