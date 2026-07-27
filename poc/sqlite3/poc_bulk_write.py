"""1000 件の書き込みを「1 トランザクション」と「件ごと commit」の 2 条件で計測する。"""

from __future__ import annotations

import logging
import sqlite3
import tempfile
import time
from contextlib import closing
from pathlib import Path

from _helpers import INSERT_TASK, open_tasks_db, setup_logging

logger = logging.getLogger(__name__)

type TaskRow = tuple[str, str, int, None]

ROW_COUNT = 1000
TIME_LIMIT_SECONDS = 1.0
PRIORITY_RANGE = 5  # priority を 0..4 で循環させる


def _build_rows(id_prefix: str) -> list[TaskRow]:
    """計測用の行を ROW_COUNT 件組み立てる。"""
    return [
        (f"{id_prefix}-{i}", f"タスク {i}", i % PRIORITY_RANGE, None) for i in range(ROW_COUNT)
    ]


def insert_in_single_transaction(conn: sqlite3.Connection, rows: list[TaskRow]) -> float:
    """executemany で 1 トランザクションにまとめて書き込み、所要秒数を返す。"""
    started = time.perf_counter()
    with conn:
        conn.executemany(INSERT_TASK, rows)
    return time.perf_counter() - started


def insert_with_commit_per_row(conn: sqlite3.Connection, rows: list[TaskRow]) -> float:
    """1 件ごとに commit して書き込み、所要秒数を返す。"""
    started = time.perf_counter()
    for row in rows:
        conn.execute(INSERT_TASK, row)
        conn.commit()  # 比較条件を作るため、行ごとに明示的に commit する
    return time.perf_counter() - started


def main() -> None:
    """同一のファイル DB に対して 2 条件の書き込み時間を計測して比較する。"""
    setup_logging()
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "tasks.db"
        with closing(open_tasks_db(db_path)) as conn:
            single_seconds = insert_in_single_transaction(conn, _build_rows("batch"))
            per_row_seconds = insert_with_commit_per_row(conn, _build_rows("each"))
            stored_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    logger.info(f"SQLite エンジン: {sqlite3.sqlite_version}")
    logger.info(f"1 トランザクション(executemany): {single_seconds:.3f} 秒 / {ROW_COUNT} 件")
    logger.info(f"件ごと commit: {per_row_seconds:.3f} 秒 / {ROW_COUNT} 件")
    logger.info(f"件ごと commit は 1 トランザクションの {per_row_seconds / single_seconds:.1f} 倍")
    logger.info(f"書き込み後の総件数: {stored_count}")
    logger.info(f"判定: {'成功' if single_seconds <= TIME_LIMIT_SECONDS else '失敗'}")


if __name__ == "__main__":
    main()
