"""単一ユースケース「タスク編集」のシナリオ E2E テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.errors import ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import get_task, update_task  # noqa: E402


def _create_task_store(*, task_id: str, title: str, content: str) -> dict[str, Task]:
    """編集対象のタスクを 1 件登録済みのストアを作る。"""
    return {task_id: Task(id=task_id, title=title, content=content)}


class TaskEditScenarioTest(unittest.TestCase):
    def test_normal(self):
        """タスクの内容を編集して保存すると一覧に編集後の内容が表示される（正常系）。"""
        # 準備
        store = _create_task_store(task_id="t1", title="旧タイトル", content="旧本文")
        # 実行
        update_task(store, "t1", "新タイトル", "新本文")
        # 検証
        listed = get_task(store, "t1")
        self.assertEqual(listed.title, "新タイトル")
        self.assertEqual(listed.content, "新本文")

    def test_error_when_title_empty(self):
        """タイトルを空にして保存すると検証に失敗し保存されない（異常系）。"""
        # 準備
        store = _create_task_store(task_id="t1", title="旧タイトル", content="旧本文")
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "", "新本文")
        # 検証（保存されていないこと）
        unchanged = get_task(store, "t1")
        self.assertEqual(unchanged.title, "旧タイトル")
        self.assertEqual(unchanged.content, "旧本文")


if __name__ == "__main__":
    unittest.main()
