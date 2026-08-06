"""複合UC「タスク編集から一覧反映」の E2E テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.errors import ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import list_tasks, update_task  # noqa: E402


def _store() -> dict[str, Task]:
    return {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}


class タスク編集から一覧反映Test(unittest.TestCase):
    def test_normal(self):
        """編集して保存すると一覧に反映される（正常系）。"""
        # 準備
        store = _store()
        # 実行
        update_task(store, "t1", "新タイトル", "新本文")
        listed = list_tasks(store)
        # 検証
        self.assertEqual(listed[0].title, "新タイトル")
        self.assertEqual(listed[0].content, "新本文")

    def test_error_when_タイトルが空(self):
        """タイトルを空にして保存すると一覧が変わらない（異常系）。"""
        # 準備
        store = _store()
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "")
        listed = list_tasks(store)
        self.assertEqual(listed[0].title, "旧タイトル")
        self.assertEqual(listed[0].content, "旧本文")


if __name__ == "__main__":
    unittest.main()
