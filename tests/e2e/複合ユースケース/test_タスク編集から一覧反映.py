"""複合UC「タスク編集から一覧反映」の E2E テスト。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from tasks.errors import ValidationError  # noqa: E402
from tasks.models import Task  # noqa: E402
from tasks.service import get_task, list_tasks, update_task  # noqa: E402


def _store() -> dict[str, Task]:
    """編集対象のタスクを 1 件登録済みのストアを作る。"""
    return {"t1": Task(id="t1", title="旧タイトル", content="旧本文")}


class タスク編集から一覧反映Test(unittest.TestCase):
    def test_normal(self):
        """編集して保存すると一覧に編集後の内容が反映される（正常系）。"""
        # 準備
        store = _store()
        # 実行
        target = get_task(store, list_tasks(store)[0].id)  # 一覧から対象タスクを選ぶ
        update_task(store, target.id, "新タイトル", "新本文")  # 編集して保存する
        listed = list_tasks(store)  # 保存完了後に一覧へ戻る
        # 検証
        self.assertEqual(listed[0].title, "新タイトル")
        self.assertEqual(listed[0].content, "新本文")

    def test_error_when_タイトルが空(self):
        """タイトルを空にして保存すると一覧が編集前のまま変わらない（異常系）。"""
        # 準備
        store = _store()
        target = get_task(store, list_tasks(store)[0].id)  # 一覧から対象タスクを選ぶ
        # 実行・検証
        with self.assertRaises(ValidationError):
            update_task(store, target.id, "")
        listed = list_tasks(store)  # 保存されないまま一覧へ戻る
        self.assertEqual(listed[0].title, "旧タイトル")
        self.assertEqual(listed[0].content, "旧本文")


if __name__ == "__main__":
    unittest.main()
