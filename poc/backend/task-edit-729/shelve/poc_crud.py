"""CRUD 観点の検証: 作成 → 書き込み → 取得 → 更新 → 削除 が一連で成功するかを確かめる。"""

from __future__ import annotations

import dbm
import logging
import shelve
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TASK_KEY = "t1"
INITIAL_TASK: dict[str, Any] = {"title": "買い物", "priority": 3, "note": None}
UPDATED_PRIORITY = 5


def run_crud(db_path: str) -> None:
    """shelve に対する CRUD 一連を実行して各段階の状態をログへ出す。"""
    # 作成 + 書き込み: shelve.open はファイルが無ければ新規作成する
    with shelve.open(db_path) as db:
        db[TASK_KEY] = INITIAL_TASK
    logger.info("[create] 書き込み完了 dbm 実装=%s", dbm.whichdb(db_path))

    # 取得
    with shelve.open(db_path) as db:
        logger.info("[read] %s", db[TASK_KEY])

    # 更新: 値をキャッシュしないため、取り出した dict を書き換えてキーへ再代入する
    with shelve.open(db_path) as db:
        task = db[TASK_KEY]
        task["priority"] = UPDATED_PRIORITY
        db[TASK_KEY] = task
    with shelve.open(db_path) as db:
        logger.info("[update] %s", db[TASK_KEY])

    # 削除
    with shelve.open(db_path) as db:
        del db[TASK_KEY]
    with shelve.open(db_path) as db:
        logger.info("[delete] キー残存=%s 総件数=%d", TASK_KEY in db, len(db))


def main() -> None:
    """一時ディレクトリに shelve を作って CRUD 検証を実行する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with tempfile.TemporaryDirectory() as tmp_dir:
        run_crud(str(Path(tmp_dir) / "tasks"))


if __name__ == "__main__":
    main()
