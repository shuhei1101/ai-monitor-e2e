"""shelve へタスクを一括書き込みしたときの所要時間を計測する。"""

from __future__ import annotations

import shelve
import sys
import tempfile
import time
from pathlib import Path

from _poc_common import Task, configure_logging, describe_store, store_path

logger = configure_logging()

STORE_STEM = "tasks"
BULK_TASK_COUNT = 1000
BULK_WRITE_LIMIT_SECONDS = 1.0
MEMO_INTERVAL = 3  # memo が None の行と文字列の行を混在させる間隔
MILLISECONDS_PER_SECOND = 1000


def _build_tasks(count: int) -> list[Task]:
    """計測用のタスクを指定件数だけ組み立てる。"""
    tasks: list[Task] = []
    for index in range(count):
        # memo は None 混在時の挙動も含めて計測するため、一定間隔で None にする
        memo = None if index % MEMO_INTERVAL == 0 else f"メモ {index}"
        tasks.append({"id": f"t-{index}", "title": f"タスク {index}", "priority": index % 5, "memo": memo})
    return tasks


def _write_all(path: str, tasks: list[Task]) -> float:
    """タスクを 1 件ずつ書き込み、書き込み開始から close 完了までの秒数を返す。"""
    with shelve.open(path) as db:
        # open は計測対象外。書き込み開始から with を抜けた時点（close 完了）までを測る
        started = time.perf_counter()
        for task in tasks:
            db[task["id"]] = task
    return time.perf_counter() - started


def _count_stored(path: str) -> int:
    """開き直して永続化されている件数を返す。"""
    with shelve.open(path) as db:
        return len(db)


def main() -> int:
    """一括書き込みを実行し、所要時間が成功条件を満たすかを判定する。"""
    tasks = _build_tasks(BULK_TASK_COUNT)

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = store_path(Path(tmp_dir), STORE_STEM)
        elapsed = _write_all(path, tasks)
        stored_count = _count_stored(path)
        logger.info("ストア情報: %s", describe_store(path))

    if stored_count != BULK_TASK_COUNT:
        raise AssertionError(f"永続化された件数が一致しない: {stored_count}/{BULK_TASK_COUNT}")

    per_task_ms = elapsed / BULK_TASK_COUNT * MILLISECONDS_PER_SECOND
    logger.info(
        "一括書き込み: %d 件 / %.4f 秒（1 件あたり %.4f ms）",
        BULK_TASK_COUNT,
        elapsed,
        per_task_ms,
    )

    # 成功条件: 書き込み開始から close 完了までが上限秒数以内
    if elapsed > BULK_WRITE_LIMIT_SECONDS:
        logger.info("一括書き込み判定: 失敗（上限 %.1f 秒を超過）", BULK_WRITE_LIMIT_SECONDS)
        return 1
    logger.info("一括書き込み判定: 成功（上限 %.1f 秒以内）", BULK_WRITE_LIMIT_SECONDS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
