from __future__ import annotations

import unittest

from src.screens.navigation import TASK_EDIT_SCREEN_ID, resolve_edit_destination, to_url
from src.screens.types import EditDestination


class ResolveEditDestinationTest(unittest.TestCase):
    """resolve_edit_destination の単体テスト。"""

    def test_resolve_edit_destination(self) -> None:
        """識別子から画面識別子 task-edit を持つ遷移先を組み立てる(正常系)。"""
        # 実行
        result = resolve_edit_destination("t2")

        # 検証
        self.assertEqual(result, EditDestination(screen_id=TASK_EDIT_SCREEN_ID, task_id="t2"))


class ToUrlTest(unittest.TestCase):
    """to_url の単体テスト。"""

    def test_to_url(self) -> None:
        """遷移先を /{画面識別子}/{タスク識別子} の URL 文字列に変換する(正常系)。"""
        # 準備
        destination = EditDestination(screen_id="task-edit", task_id="t2")

        # 実行
        result = to_url(destination)

        # 検証
        self.assertEqual(result, "/task-edit/t2")

    def test_to_url_when_task_id_contains_separator(self) -> None:
        """識別子に区切り文字が含まれるとパーセントエンコードしてパスの構造を保つ(正常系)。"""
        # 準備
        destination = EditDestination(screen_id="task-edit", task_id="a/b")

        # 実行
        result = to_url(destination)

        # 検証
        self.assertEqual(result, "/task-edit/a%2Fb")


if __name__ == "__main__":
    unittest.main()
