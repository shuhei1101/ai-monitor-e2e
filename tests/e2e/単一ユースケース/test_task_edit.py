"""単一ユースケースシナリオ「タスク編集」の E2E テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.errors import ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import list_tasks, update_task  # noqa: E402

TARGET_TASK_ID = "t1"


def _create_store_with_task() -> dict[str, Task]:
    """編集対象のタスクを 1 件登録済みのストアを作る。"""
    return {TARGET_TASK_ID: Task(id=TARGET_TASK_ID, title="編集前タイトル", content="編集前本文")}


class TaskEditTest(unittest.TestCase):
    def test_normal(self):
        """編集した内容で保存すると一覧に反映される（正常系）。"""
        # 準備
        store = _create_store_with_task()
        # 実行
        update_task(store, TARGET_TASK_ID, "編集後タイトル", "編集後本文")
        # 検証
        listed = list_tasks(store)
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].title, "編集後タイトル")
        self.assertEqual(listed[0].content, "編集後本文")

    def test_error_when_title_empty(self):
        """タイトルを空にして保存すると検証エラーになり保存されない（異常系）。"""
        # 準備
        store = _create_store_with_task()
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, TARGET_TASK_ID, "", "編集後本文")
        listed = list_tasks(store)
        self.assertEqual(listed[0].title, "編集前タイトル")
        self.assertEqual(listed[0].content, "編集前本文")


if __name__ == "__main__":
    unittest.main()
