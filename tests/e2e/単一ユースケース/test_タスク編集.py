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

    def test_error_when_title_empty(self):
        """タイトルを空にして保存するとインラインエラーになり保存されない（異常系）。"""
        # 準備
        store = _store()
        original_title = store["t1"].title
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "")
        # 検証: 旧タイトルのまま保存されていない
        self.assertEqual(store["t1"].title, original_title)


if __name__ == "__main__":
    unittest.main()
