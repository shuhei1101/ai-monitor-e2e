"""str / int / None / bool を tasks スキーマへ書き込み、取り出した値の型を確認する。"""

from __future__ import annotations

import logging
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from _helpers import INSERT_TASK, SELECT_TASK, open_tasks_db, setup_logging

logger = logging.getLogger(__name__)

PROBE_ID = "type-probe"
PROBE_TITLE = "型の往復を確認する"
PROBE_PRIORITY = 3
BOOL_PROBE_ID = "bool-probe"
BOOL_PROBE_VALUE = True


def _log_roundtrip(column: str, sent: object, got: object) -> bool:
    """1 カラム分の書き込み型と取得型を出力し、一致したかを返す。"""
    matched = type(sent) is type(got)
    logger.info(
        f"{column}: 書き込み {type(sent).__name__}({sent!r}) -> "
        f"取得 {type(got).__name__}({got!r}) / 一致: {matched}"
    )
    return matched


def main() -> None:
    """tasks の各カラム型に値を通して、往復後の Python 型を観測する。"""
    setup_logging()
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "tasks.db"
        with closing(open_tasks_db(db_path)) as conn:
            with conn:
                conn.execute(INSERT_TASK, (PROBE_ID, PROBE_TITLE, PROBE_PRIORITY, None))
                # bool 専用のカラム型は無いため、INTEGER 列（priority）へ入れて戻り型を見る
                conn.execute(INSERT_TASK, (BOOL_PROBE_ID, PROBE_TITLE, BOOL_PROBE_VALUE, None))

            row = conn.execute(SELECT_TASK, (PROBE_ID,)).fetchone()
            bool_row = conn.execute(SELECT_TASK, (BOOL_PROBE_ID,)).fetchone()

    required = [
        _log_roundtrip("id (TEXT) / str", PROBE_ID, row[0]),
        _log_roundtrip("title (TEXT) / str", PROBE_TITLE, row[1]),
        _log_roundtrip("priority (INTEGER) / int", PROBE_PRIORITY, row[2]),
        _log_roundtrip("note (TEXT) / None", None, row[3]),
    ]
    # bool は成功条件に含まれない参考値なので判定には入れない
    _log_roundtrip("priority (INTEGER) / bool", BOOL_PROBE_VALUE, bool_row[2])

    logger.info(f"判定: {'成功' if all(required) else '失敗'}")


if __name__ == "__main__":
    main()
