"""観点 2: 大量件数の一括書き込みが制限時間内に完了するかを検証する。"""

from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path

from poc.sqlite3 import db
from poc.sqlite3._helpers import mark
from poc.sqlite3.config import load_config
from poc.sqlite3.types import Task

logger = logging.getLogger(__name__)

# 優先度は 1〜3 を循環させる（値のばらつきを持たせるため）
PRIORITY_CYCLE = 3


def run() -> bool:
    """一括書き込みの所要秒数を計測し、制限時間内に収まったかを返す。"""
    config = load_config()
    tasks = [_build_task(index) for index in range(config.bulk_write.record_count)]

    with tempfile.TemporaryDirectory() as tmp_dir:
        conn = db.connect(str(Path(tmp_dir) / config.db_filename))
        try:
            # 計測範囲は書き込み開始から永続化の確定（commit 完了）まで
            started_at = time.perf_counter()
            db.create_tasks(conn, tasks)
            elapsed_sec = time.perf_counter() - started_at

            stored_count = db.count_tasks(conn)
        finally:
            conn.close()

    stored_ok = stored_count == config.bulk_write.record_count
    within_limit = elapsed_sec <= config.bulk_write.time_limit_sec

    logger.info(
        "書き込み件数: %d 件（DB 上の件数: %d 件） %s",
        config.bulk_write.record_count,
        stored_count,
        mark(stored_ok),
    )
    logger.info(
        "所要時間: %.3f 秒（上限 %.1f 秒） %s",
        elapsed_sec,
        config.bulk_write.time_limit_sec,
        mark(within_limit),
    )

    # commit のまとめ方で所要時間がどれだけ変わるかを参考値として出す
    per_record_sec = _measure_per_record_commit(tasks, config.db_filename)
    logger.info(
        "参考: 1 件ずつ commit した場合 %.3f 秒（一括の %.1f 倍）",
        per_record_sec,
        per_record_sec / elapsed_sec,
    )

    return stored_ok and within_limit


def _measure_per_record_commit(tasks: list[Task], db_filename: str) -> float:
    """1 件ずつ commit した場合の所要秒数を計測する（判定には使わない参考値）。"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        conn = db.connect(str(Path(tmp_dir) / db_filename))
        try:
            started_at = time.perf_counter()
            for task in tasks:
                db.create_task(conn, task)
            return time.perf_counter() - started_at
        finally:
            conn.close()


def _build_task(index: int) -> Task:
    """連番からダミーのタスクを 1 件組み立てる。"""
    return Task(
        id=f"t-{index:04d}",
        title=f"タスク {index}",
        priority=index % PRIORITY_CYCLE + 1,
        # 偶数番だけメモを持たせて NULL 混在の状態にする
        memo=f"メモ {index}" if index % 2 == 0 else None,
    )
