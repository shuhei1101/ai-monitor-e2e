"""sqlite3 PoC の 3 観点をまとめて実行する。"""

from __future__ import annotations

import logging
import sqlite3
import sys

from poc.sqlite3 import poc_bulk_write, poc_crud, poc_type_roundtrip
from poc.sqlite3._helpers import mark

logger = logging.getLogger(__name__)

CHECKS = (
    ("CRUD", poc_crud.run),
    ("一括書き込みの性能", poc_bulk_write.run),
    ("型の往復", poc_type_roundtrip.run),
)


def main() -> int:
    """全観点を実行し、1 つでも失敗したら終了コード 1 を返す。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("Python: %s", sys.version.split()[0])
    logger.info("sqlite_version: %s", sqlite3.sqlite_version)

    results = []
    for name, run_check in CHECKS:
        logger.info("")
        logger.info("=== 観点: %s ===", name)
        results.append((name, run_check()))

    logger.info("")
    logger.info("=== 判定サマリ ===")
    for name, ok in results:
        logger.info("%s: %s", name, mark(ok))

    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
