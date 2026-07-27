"""観点 1: 作成 → 書き込み → 取得 → 更新 → 削除 が一連で成功するかを検証する。"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from poc.sqlite3 import db
from poc.sqlite3._helpers import mark
from poc.sqlite3.config import load_config
from poc.sqlite3.types import Task

logger = logging.getLogger(__name__)

INITIAL_TASK = Task(id="t-1", title="買い物", priority=3, memo=None)
UPDATED_TASK = Task(id="t-1", title="買い物（週末）", priority=1, memo="牛乳と卵")


def run() -> bool:
    """CRUD を一連で実行し、各ステップの結果をログに出して成否を返す。"""
    config = load_config()

    with tempfile.TemporaryDirectory() as tmp_dir:
        conn = db.connect(str(Path(tmp_dir) / config.db_filename))
        try:
            # 作成 + 書き込み: INSERT した内容がそのまま取り出せるか
            db.create_task(conn, INITIAL_TASK)
            created = db.find_task(conn, INITIAL_TASK.id)
            created_ok = created == INITIAL_TASK
            logger.info("作成 + 取得: %s（取得値: %s）", mark(created_ok), created)

            # 更新: UPDATE した内容が反映されるか
            db.update_task(conn, UPDATED_TASK)
            updated = db.find_task(conn, UPDATED_TASK.id)
            updated_ok = updated == UPDATED_TASK
            logger.info("更新 + 取得: %s（取得値: %s）", mark(updated_ok), updated)

            # 削除: DELETE 後に取得できなくなるか
            db.delete_task(conn, INITIAL_TASK.id)
            deleted = db.find_task(conn, INITIAL_TASK.id)
            deleted_ok = deleted is None
            logger.info("削除 + 取得: %s（取得値: %s）", mark(deleted_ok), deleted)
        finally:
            conn.close()

    return created_ok and updated_ok and deleted_ok
