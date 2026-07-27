"""`src/tasks/service.py` の単体テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tasks.errors import TaskNotFoundError, ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import get_task, list_tasks, update_task  # noqa: E402


def _store() -> dict[str, Task]:
    return {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}


class UpdateTaskTest(unittest.TestCase):
    def test_update_task(self):
        """タイトルと本文を更新する（正常系）。"""
        store = _store()
        result = update_task(store, "t1", "新タイトル", "新本文")
        self.assertEqual(result.title, "新タイトル")
        self.assertEqual(result.content, "新本文")
        self.assertEqual(store["t1"].title, "新タイトル")

    def test_update_task_when_content_omitted(self):
        """本文を省略すると空文字になる（正常系）。"""
        store = _store()
        result = update_task(store, "t1", "新タイトル")
        self.assertEqual(result.content, "")

    def test_update_task_when_title_empty(self):
        """タイトルが空なら ValidationError（異常系）。"""
        store = _store()
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "")

    def test_update_task_when_title_too_long(self):
        """タイトルが 101 文字なら ValidationError（異常系）。"""
        store = _store()
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "a" * 101)

    def test_update_task_when_content_too_long(self):
        """本文が 1001 文字なら ValidationError（異常系）。"""
        store = _store()
        with self.assertRaises(ValidationError):
            update_task(store, "t1", "新タイトル", "a" * 1001)

    def test_update_task_when_task_missing(self):
        """未登録の task_id なら TaskNotFoundError（異常系）。"""
        store = _store()
        with self.assertRaises(TaskNotFoundError):
            update_task(store, "missing", "新タイトル")
        self.assertEqual(store["t1"].title, "旧タイトル")


class GetTaskTest(unittest.TestCase):
    def test_get_task(self):
        """登録済みの task_id でタスクを 1 件取得する（正常系）。"""
        store = _store()
        result = get_task(store, "t1")
        self.assertEqual(result.title, "旧タイトル")

    def test_get_task_when_task_missing(self):
        """未登録の task_id なら TaskNotFoundError（異常系）。"""
        store = _store()
        with self.assertRaises(TaskNotFoundError):
            get_task(store, "missing")


class ListTasksTest(unittest.TestCase):
    def test_list_tasks(self):
        """ストアのタスクを ID 順で一覧にする（正常系）。"""
        store = _store()
        store["t0"] = Task(id="t0", title="先頭タイトル", content="先頭本文")
        result = list_tasks(store)
        self.assertEqual([task.id for task in result], ["t0", "t1"])


if __name__ == "__main__":
    unittest.main()
