"""単一UC「タスク編集」の E2E テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.models import Task  # noqa: E402
from tasks.service import list_tasks, update_task  # noqa: E402


def _store() -> dict[str, Task]:
    return {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}


class タスク編集Test(unittest.TestCase):
    def test_normal(self):
        """一覧から選んだタスクを編集して保存する（正常系）。"""
        # 準備
        store = _store()
        # 実行
        update_task(store, "t1", "新タイトル", "新本文")
        listed = list_tasks(store)
        # 検証
        self.assertEqual(listed[0].title, "新タイトル")
        self.assertEqual(listed[0].content, "新本文")

    def test_normal_when_タイトルが空(self):
        """タイトルを空にして保存すると空タイトルのまま一覧に表示される（正常系）。"""
        # 準備
        store = _store()
        # 実行
        update_task(store, "t1", "")
        listed = list_tasks(store)
        # 検証
        self.assertEqual(listed[0].title, "")


if __name__ == "__main__":
    unittest.main()
