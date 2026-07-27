"""型の往復観点の検証: str / int / None が同じ型で取り出せるか、およびネスト値の更新挙動を確かめる。"""

from __future__ import annotations

import logging
import shelve
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TASK_KEY = "t1"
SAMPLE_TASK: dict[str, Any] = {"title": "買い物", "priority": 3, "note": None}
NESTED_PRIORITY = 99


def check_type_roundtrip(db_path: str) -> None:
    """各フィールドの型が書き込み前後で一致するかをログへ出す。"""
    with shelve.open(db_path) as db:
        db[TASK_KEY] = SAMPLE_TASK

    with shelve.open(db_path) as db:
        loaded = db[TASK_KEY]

    for field, before in SAMPLE_TASK.items():
        after = loaded[field]
        # 型が一致し、かつ値も一致して初めて往復成功とみなす
        matched = type(after) is type(before) and after == before
        logger.info(
            "[%s] 書き込み前=%r(%s) 取り出し後=%r(%s) 一致=%s",
            field,
            before,
            type(before).__name__,
            after,
            type(after).__name__,
            matched,
        )


def check_nested_inplace_update(db_path: str) -> None:
    """writeback 未指定でネストした値をインプレース変更した場合に保存されるかをログへ出す。"""
    with shelve.open(db_path) as db:
        db[TASK_KEY] = SAMPLE_TASK

    # 取り出した dict を直接書き換えるだけで再代入しない（writeback 未指定）
    with shelve.open(db_path) as db:
        db[TASK_KEY]["priority"] = NESTED_PRIORITY

    with shelve.open(db_path) as db:
        logger.info(
            "[nested] インプレース変更後の priority=%r (期待した変更値=%r)",
            db[TASK_KEY]["priority"],
            NESTED_PRIORITY,
        )


def main() -> None:
    """一時ディレクトリに shelve を作って型往復とネスト更新の検証を実行する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        check_type_roundtrip(str(tmp / "types"))
        check_nested_inplace_update(str(tmp / "nested"))


if __name__ == "__main__":
    main()
