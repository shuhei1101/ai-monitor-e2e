"""shelve の CRUD（作成 / 取得 / 更新 / 削除）を一連で検証する。"""

from __future__ import annotations

import shelve
import sys
import tempfile
from pathlib import Path

from _poc_common import Task, configure_logging, describe_store, store_path

logger = configure_logging()

STORE_STEM = "tasks"
INITIAL_TASK: Task = {"id": "t-1", "title": "買い物", "priority": 3, "memo": None}
UPDATED_TITLE = "買い物（週末）"
UPDATED_PRIORITY = 1
UPDATED_MEMO = "牛乳と卵"


def _create(path: str) -> None:
    """タスクを 1 件書き込む。"""
    with shelve.open(path) as db:
        db[INITIAL_TASK["id"]] = INITIAL_TASK


def _read(path: str) -> Task:
    """書き込んだタスクを開き直して取得する。"""
    with shelve.open(path) as db:
        return db[INITIAL_TASK["id"]]


def _update_in_place(path: str) -> None:
    """取り出した dict を書き戻さずに書き換える（writeback=False の挙動確認用）。"""
    with shelve.open(path) as db:
        task: Task = db[INITIAL_TASK["id"]]
        task["title"] = UPDATED_TITLE


def _update(path: str) -> None:
    """取り出した dict を書き換えてキーへ代入し直す。"""
    with shelve.open(path) as db:
        task: Task = db[INITIAL_TASK["id"]]
        task["title"] = UPDATED_TITLE
        task["priority"] = UPDATED_PRIORITY
        task["memo"] = UPDATED_MEMO
        db[INITIAL_TASK["id"]] = task


def _delete(path: str) -> bool:
    """タスクを削除し、削除後にキーが残っていないかを返す。"""
    with shelve.open(path) as db:
        del db[INITIAL_TASK["id"]]
    with shelve.open(path) as db:
        return INITIAL_TASK["id"] in db


def main() -> int:
    """CRUD を順に実行し、各段階の結果を検証する。"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = store_path(Path(tmp_dir), STORE_STEM)

        # 作成: 新規タスクを書き込む
        _create(path)
        logger.info("ストア情報: %s", describe_store(path))
        logger.info("作成: %s を書き込み", INITIAL_TASK["id"])

        # 取得: 別セッションで開き直し、書き込んだ内容がそのまま戻るかを見る
        stored = _read(path)
        if stored != INITIAL_TASK:
            raise AssertionError(f"取得した値が書き込んだ値と一致しない: {stored}")
        logger.info("取得: %s", stored)

        # 更新（書き戻しなし）: 取り出した dict の in-place 変更が永続化されるかを見る
        _update_in_place(path)
        in_place_persisted = _read(path)["title"] == UPDATED_TITLE
        logger.info("in-place 変更の永続化: %s", in_place_persisted)

        # 更新（書き戻しあり）: キーへ代入し直した内容が永続化されるかを見る
        _update(path)
        updated = _read(path)
        expected: Task = {
            "id": INITIAL_TASK["id"],
            "title": UPDATED_TITLE,
            "priority": UPDATED_PRIORITY,
            "memo": UPDATED_MEMO,
        }
        if updated != expected:
            raise AssertionError(f"更新後の値が期待値と一致しない: {updated}")
        logger.info("更新: %s", updated)

        # 削除: キーごと消えているかを見る
        remains = _delete(path)
        if remains:
            raise AssertionError("削除後もキーが残っている")
        logger.info("削除: キー %s は存在しない", INITIAL_TASK["id"])

    logger.info("CRUD 判定: 成功（作成 → 取得 → 更新 → 削除 が一連で成功）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
