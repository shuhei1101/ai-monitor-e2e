"""一括書き込みの性能観点の検証: 1000 件の書き込み時間を open 回数の 2 条件で計測する。"""

from __future__ import annotations

import logging
import shelve
import tempfile
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TASK_COUNT = 1000
SUCCESS_THRESHOLD_SEC = 1.0
PRIORITY_RANGE = 5


def _make_task(index: int) -> dict[str, Any]:
    """計測用のタスク 1 件分を作る。"""
    return {"title": f"タスク{index}", "priority": index % PRIORITY_RANGE, "note": None}


def write_in_single_open(db_path: str) -> float:
    """shelve.open を 1 回にまとめて全件書き込み、所要秒数を返す。"""
    start = time.perf_counter()
    with shelve.open(db_path) as db:
        for i in range(TASK_COUNT):
            db[f"t{i}"] = _make_task(i)
    return time.perf_counter() - start


def write_per_record_open(db_path: str) -> float:
    """1 件ごとに shelve.open し直して全件書き込み、所要秒数を返す。"""
    start = time.perf_counter()
    # 1 件ごとに open / close するため、close 時のフラッシュが件数分発生する
    for i in range(TASK_COUNT):
        with shelve.open(db_path) as db:
            db[f"t{i}"] = _make_task(i)
    return time.perf_counter() - start


def _log_result(condition: str, elapsed_sec: float) -> None:
    """計測結果と成功条件（1 秒以内）に対する判定をログへ出す。"""
    verdict = "OK" if elapsed_sec <= SUCCESS_THRESHOLD_SEC else "NG"
    logger.info("[%s] %d 件 %.3f 秒 (閾値 %.1f 秒: %s)", condition, TASK_COUNT, elapsed_sec, SUCCESS_THRESHOLD_SEC, verdict)


def main() -> None:
    """2 条件それぞれを独立した shelve ファイルで計測する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        _log_result("open 1 回", write_in_single_open(str(tmp / "bulk_single")))
        _log_result("件ごとに open", write_per_record_open(str(tmp / "bulk_per_record")))


if __name__ == "__main__":
    main()
