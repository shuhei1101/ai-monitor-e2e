"""1000 件の一括挿入にかかる時間を実測する。"""
from __future__ import annotations

import logging
import time

from poc.db import connect_tasks_db, setup_logger

logger = logging.getLogger(__name__)

INSERT_COUNT = 1000
INSERT_SQL = "INSERT INTO tasks VALUES (?, ?, ?)"


def _rows() -> list[tuple[str, str, str]]:
    """挿入する 1000 件分のタスク行を組み立てる。"""
    return [(f"t{i}", f"タスク{i}", f"本文{i}") for i in range(INSERT_COUNT)]


def _measure_executemany() -> float:
    """executemany で一括挿入したときの所要秒数を返す。"""
    conn = connect_tasks_db()
    rows = _rows()
    started = time.perf_counter()
    conn.executemany(INSERT_SQL, rows)
    conn.commit()
    elapsed = time.perf_counter() - started
    stored = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    logger.info("executemany: %s 件 %.4f 秒", stored, elapsed)
    conn.close()
    return elapsed


def _measure_execute_loop() -> float:
    """1 件ずつ execute したときの所要秒数を返す。"""
    conn = connect_tasks_db()
    rows = _rows()
    started = time.perf_counter()
    # 1 件ずつ実行し、commit は最後に 1 回だけ行う
    for row in rows:
        conn.execute(INSERT_SQL, row)
    conn.commit()
    elapsed = time.perf_counter() - started
    stored = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    logger.info("execute ループ: %s 件 %.4f 秒", stored, elapsed)
    conn.close()
    return elapsed


def main() -> None:
    """一括挿入と 1 件ずつ挿入の 2 通りで所要時間を測る。"""
    setup_logger()
    _measure_executemany()
    _measure_execute_loop()


if __name__ == "__main__":
    main()
