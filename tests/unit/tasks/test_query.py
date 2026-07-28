from __future__ import annotations

import unittest

from src.tasks.errors import TaskNotFoundError, ValidationError
from src.tasks.query import (
    TASK_ID_MAX_LENGTH,
    TASK_ID_MIN_LENGTH,
    _validate_task_id,
    get_task,
)
from src.tasks.types import Task, TaskStore


class GetTaskTest(unittest.TestCase):
    """get_task の単体テスト。"""

    def test_get_task(self) -> None:
        """登録済みの識別子で 1 件返す(正常系)。"""
        # 準備
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}
        store_snapshot = dict(store)

        # 実行
        result = get_task(store, "t1")

        # 検証: 保管先の内容が変化していない
        self.assertEqual(result, store["t1"])
        self.assertEqual(store, store_snapshot)

    def test_get_task_when_id_unregistered(self) -> None:
        """未登録の識別子を指定すると TaskNotFoundError を送出する(異常系)。"""
        # 準備
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}

        # 実行・検証
        with self.assertRaises(TaskNotFoundError):
            get_task(store, "t9")

    def test_get_task_when_id_empty(self) -> None:
        """識別子が空文字だと ValidationError を送出する(異常系)。"""
        # 準備
        store: TaskStore = {"t1": Task(id="t1", title="買い物リストの作成")}

        # 実行・検証
        with self.assertRaises(ValidationError):
            get_task(store, "")


class ValidateTaskIdTest(unittest.TestCase):
    """_validate_task_id の単体テスト。"""

    def test_validate_task_id_when_min_length(self) -> None:
        """下限ちょうどの識別子は例外を送出しない(正常系)。"""
        # 実行・検証
        _validate_task_id("t" * TASK_ID_MIN_LENGTH)

    def test_validate_task_id_when_max_length(self) -> None:
        """上限ちょうどの識別子は例外を送出しない(正常系)。"""
        # 実行・検証
        _validate_task_id("t" * TASK_ID_MAX_LENGTH)

    def test_validate_task_id_when_empty(self) -> None:
        """下限未満の識別子は判定条件と一致したメッセージで ValidationError を送出する(異常系)。"""
        # 実行・検証
        with self.assertRaises(ValidationError) as ctx:
            _validate_task_id("")
        self.assertIn(str(TASK_ID_MIN_LENGTH), str(ctx.exception))
        self.assertIn(str(TASK_ID_MAX_LENGTH), str(ctx.exception))

    def test_validate_task_id_when_over_max_length(self) -> None:
        """上限超過の識別子は判定条件と一致したメッセージで ValidationError を送出する(異常系)。"""
        # 実行・検証
        with self.assertRaises(ValidationError) as ctx:
            _validate_task_id("t" * (TASK_ID_MAX_LENGTH + 1))
        self.assertIn(str(TASK_ID_MIN_LENGTH), str(ctx.exception))
        self.assertIn(str(TASK_ID_MAX_LENGTH), str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
