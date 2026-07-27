"""shelve に書き込んだ値が同じ型で取り出せるか（型の往復）を検証する。"""

from __future__ import annotations

import shelve
import sys
import tempfile
from pathlib import Path

from _poc_common import Task, configure_logging, describe_store, store_path

logger = configure_logging()

STORE_STEM = "tasks"
ROUNDTRIP_TASK: Task = {"id": "t-roundtrip", "title": "型往復の確認", "priority": 5, "memo": None}
INVALID_KEY = 1  # キーが str 固定であることを確認するための int キー


def _roundtrip(path: str, task: Task) -> Task:
    """タスクを書き込み、開き直して取り出す。"""
    with shelve.open(path) as db:
        db[task["id"]] = task
    with shelve.open(path) as db:
        return db[task["id"]]


def _check_int_key(path: str) -> str:
    """int キーで書き込みを試し、発生した例外の内容を返す。"""
    with shelve.open(path) as db:
        try:
            db[INVALID_KEY] = ROUNDTRIP_TASK  # type: ignore[index]
        except (TypeError, AttributeError) as e:
            # shelve はキーを内部で encode するため、str 以外は encode 時に落ちる
            return f"{type(e).__name__}: {e}"
    return "例外なし（int キーが受理された）"


def main() -> int:
    """書き込み前後の型を突き合わせ、成功条件を満たすかを判定する。"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = store_path(Path(tmp_dir), STORE_STEM)
        restored = _roundtrip(path, ROUNDTRIP_TASK)
        logger.info("ストア情報: %s", describe_store(path))
        int_key_result = _check_int_key(path)

    mismatches: list[str] = []
    for field, original in ROUNDTRIP_TASK.items():
        restored_value = restored[field]
        logger.info(
            "%s: 書き込み %r (%s) → 取り出し %r (%s)",
            field,
            original,
            type(original).__name__,
            restored_value,
            type(restored_value).__name__,
        )
        # 型と値の両方が一致して初めて往復できたとみなす
        if type(restored_value) is not type(original) or restored_value != original:
            mismatches.append(field)

    logger.info("int キーでの書き込み: %s", int_key_result)

    if mismatches:
        logger.info("型の往復判定: 失敗（不一致フィールド: %s）", ", ".join(mismatches))
        return 1
    logger.info("型の往復判定: 成功（str / int / None が同じ型で復元）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
