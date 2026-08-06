"""単一ユースケース「タスク編集」のシナリオ E2E テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.errors import ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import list_tasks, update_task  # noqa: E402

TARGET_TASK_ID = "t1"


def _store_with_task() -> dict[str, Task]:
    """編集対象のタスクを 1 件登録済みのストアを作る。"""
    return {TARGET_TASK_ID: Task(id=TARGET_TASK_ID, title="編集前タイトル", content="編集前本文")}


class TaskEditScenarioTest(unittest.TestCase):
    def test_normal(self):
        """編集した内容で保存すると一覧に編集後の内容が並ぶ（正常系）。"""
        # 準備
        store = _store_with_task()
        # 実行
        update_task(store, TARGET_TASK_ID, "編集後タイトル", "編集後本文")
        listed = list_tasks(store)
        # 検証
        self.assertEqual([task.title for task in listed], ["編集後タイトル"])
        self.assertEqual([task.content for task in listed], ["編集後本文"])

    def test_error_when_title_empty(self):
        """タイトルを空にして保存すると検証に失敗し保存されない（異常系）。"""
        # 準備
        store = _store_with_task()
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, TARGET_TASK_ID, "", "編集後本文")
        listed = list_tasks(store)
        self.assertEqual([task.title for task in listed], ["編集前タイトル"])
        self.assertEqual([task.content for task in listed], ["編集前本文"])


if __name__ == "__main__":
    unittest.main()
