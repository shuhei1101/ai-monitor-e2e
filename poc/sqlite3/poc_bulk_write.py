"""sqlite3 で 1000 件の一括書き込みが 1 秒以内に完了するかを実測する。"""

from __future__ import annotations

import logging
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from _schema import INSERT_TASK, connect_with_schema

logger = logging.getLogger(__name__)

BULK_ROW_COUNT = 1000
TIME_LIMIT_SECONDS = 1.0
PRIORITY_RANGE = 5


@dataclass(frozen=True, slots=True, kw_only=True)
class BulkWriteResult:
    """一括書き込みの実測結果。"""

    elapsed_seconds: float
    stored_count: int


def measure_bulk_insert(db_path: Path, row_count: int) -> BulkWriteResult:
    """executemany + 単一トランザクションで row_count 件書き込み、経過秒数と保存件数を返す。"""
    conn = connect_with_schema(db_path)
    rows = [(f"t{i}", f"タスク{i}", i % PRIORITY_RANGE, None) for i in range(row_count)]

    # 計測対象は executemany と commit のみ（行データの生成は計測前に済ませる）
    started = time.perf_counter()
    conn.executemany(INSERT_TASK, rows)
    conn.commit()
    elapsed_seconds = time.perf_counter() - started

    stored_count = int(conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])
    conn.close()
    return BulkWriteResult(elapsed_seconds=elapsed_seconds, stored_count=stored_count)


def main() -> None:
    """一時ディレクトリに DB ファイルを作って一括書き込みを計測する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = measure_bulk_insert(Path(tmp_dir) / "tasks.db", BULK_ROW_COUNT)

    within_limit = result.elapsed_seconds <= TIME_LIMIT_SECONDS
    logger.info("[一括書き込み] 件数=%d 保存件数=%d", BULK_ROW_COUNT, result.stored_count)
    logger.info(
        "[一括書き込み] 経過=%.4f 秒 上限=%.1f 秒 判定=%s",
        result.elapsed_seconds,
        TIME_LIMIT_SECONDS,
        "成功条件を満たす" if within_limit else "成功条件を満たさない",
    )


if __name__ == "__main__":
    main()
