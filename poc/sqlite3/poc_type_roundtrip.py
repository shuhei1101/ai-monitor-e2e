"""観点 3: str / int / None が書き込み時と同じ型で取り出せるかを検証する。"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import fields
from pathlib import Path

from poc.sqlite3 import db
from poc.sqlite3._helpers import mark
from poc.sqlite3.config import load_config
from poc.sqlite3.types import Task

logger = logging.getLogger(__name__)

# memo が NULL のケースと TEXT のケースの両方で型を確認する
TASK_WITH_NULL_MEMO = Task(id="t-null", title="メモなし", priority=2, memo=None)
TASK_WITH_TEXT_MEMO = Task(id="t-text", title="メモあり", priority=5, memo="買い出しリスト")


def run() -> bool:
    """書き込み前後で各フィールドの型が一致するかをログに出して成否を返す。"""
    config = load_config()
    all_ok = True

    with tempfile.TemporaryDirectory() as tmp_dir:
        conn = db.connect(str(Path(tmp_dir) / config.db_filename))
        try:
            for written in (TASK_WITH_NULL_MEMO, TASK_WITH_TEXT_MEMO):
                db.create_task(conn, written)
                loaded = db.find_task(conn, written.id)
                # 取得できない時点で型の比較以前に失敗
                if loaded is None:
                    logger.info("%s: 取得できず %s", written.id, mark(False))
                    all_ok = False
                    continue

                all_ok = _log_type_diff(written, loaded) and all_ok
        finally:
            conn.close()

    return all_ok


def _log_type_diff(written: Task, loaded: Task) -> bool:
    """フィールドごとに書き込み時と読み出し後の型を突き合わせてログに出す。"""
    matched = True
    for field in fields(Task):
        written_type = type(getattr(written, field.name)).__name__
        loaded_type = type(getattr(loaded, field.name)).__name__
        field_ok = written_type == loaded_type
        matched = matched and field_ok
        logger.info(
            "%s.%s: 書き込み %s → 取得 %s %s",
            written.id,
            field.name,
            written_type,
            loaded_type,
            mark(field_ok),
        )
    return matched
