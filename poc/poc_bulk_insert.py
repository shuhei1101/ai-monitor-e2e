"""1000 件の一括挿入が制限時間内に収まるかを計測する。"""
from __future__ import annotations

import sqlite3
import time

from _schema import INSERT_TASK_SQL, build_logger, open_memory_db

ROW_COUNT = 1000
TIME_LIMIT_SECONDS = 1.0
PRIORITY_VARIATION = 3

logger = build_logger(__name__)


def _build_rows() -> list[tuple[str, str, str, int]]:
    """挿入する 1000 件分の行を組み立てる。"""
    return [(f"t{i}", f"タスク{i}", f"本文{i}", i % PRIORITY_VARIATION) for i in range(ROW_COUNT)]


def _measure(conn: sqlite3.Connection, rows: list[tuple[str, str, str, int]], *, bulk: bool) -> float:
    """挿入から commit までの所要秒数を返す。"""
    started = time.perf_counter()
    # executemany と 1 件ずつの execute で所要時間が変わるため両方を計る
    if bulk:
        conn.executemany(INSERT_TASK_SQL, rows)
    else:
        for row in rows:
            conn.execute(INSERT_TASK_SQL, row)
    conn.commit()
    return time.perf_counter() - started


def main() -> None:
    """executemany と逐次 execute の挿入時間を計測してログへ出す。"""
    rows = _build_rows()

    bulk_conn = open_memory_db()
    bulk_seconds = _measure(bulk_conn, rows, bulk=True)
    inserted = bulk_conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    bulk_conn.close()

    each_conn = open_memory_db()
    each_seconds = _measure(each_conn, rows, bulk=False)
    each_conn.close()

    logger.info(f"挿入件数: {inserted} 件（上限 {TIME_LIMIT_SECONDS} 秒）")
    logger.info(f"executemany: {bulk_seconds:.4f} 秒")
    logger.info(f"execute 逐次: {each_seconds:.4f} 秒")


if __name__ == "__main__":
    main()
