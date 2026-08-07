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
        """編集して保存すると一覧に編集後のタイトルと本文が並ぶ（正常系）。"""
        # 準備
        store = _store()
        # 実行
        # 一覧から対象タスクを選ぶ
        selected = get_task(store, "t1")
        # 単一UC「タスク編集」の正常シナリオを通す
        update_task(store, selected.id, "新タイトル", "新本文")
        # 保存完了後に一覧へ戻る
        listed = list_tasks(store)
        # 検証
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].title, "新タイトル")
        self.assertEqual(listed[0].content, "新本文")

    def test_error_when_タイトルが空(self):
        """タイトルを空にして保存すると一覧が編集前のまま変わらない（異常系）。"""
        # 準備
        store = _store()
        selected = get_task(store, "t1")
        # 実行・検証
        # 単一UC「タスク編集」の異常シナリオ（タイトルが空）で保存が弾かれる
        with self.assertRaises(ValidationError):
            update_task(store, selected.id, "")
        # 一覧へ戻っても編集前の内容のまま
        listed = list_tasks(store)
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].title, "旧タイトル")
        self.assertEqual(listed[0].content, "旧本文")


if __name__ == "__main__":
    unittest.main()
