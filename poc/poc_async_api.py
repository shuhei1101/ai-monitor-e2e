"""sqlite3 が await 可能なクエリ API を標準で提供するかを実測する。"""
from __future__ import annotations

import asyncio
import inspect
import logging
import sqlite3

from poc.db import connect_tasks_db, setup_logger

logger = logging.getLogger(__name__)

PROBE_SQL = "SELECT 1"


def _find_coroutine_functions() -> list[str]:
    """sqlite3 モジュールと Connection / Cursor の公開 API からコルーチン関数を集める。"""
    found: list[str] = []
    targets: list[tuple[str, object]] = [
        ("sqlite3", sqlite3),
        ("Connection", sqlite3.Connection),
        ("Cursor", sqlite3.Cursor),
    ]
    for label, target in targets:
        for name in dir(target):
            # 非公開シンボルは API として提供されていないので数えない
            if name.startswith("_"):
                continue
            if inspect.iscoroutinefunction(getattr(target, name)):
                found.append(f"{label}.{name}")
    return found


async def _await_execute() -> str:
    """execute の戻り値を await した結果、または送出された例外を文字列で返す。"""
    conn = connect_tasks_db()
    try:
        await conn.execute(PROBE_SQL)  # type: ignore[misc]
    except TypeError as e:
        # await 不可であること自体が実測値なので、型と文言を残す
        return f"{type(e).__name__}: {e}"
    finally:
        conn.close()
    return "await 成功"


def main() -> None:
    """コルーチン関数の有無と await の可否を出力する。"""
    setup_logger()
    logger.info("コルーチン関数: %s", _find_coroutine_functions() or "なし")
    logger.info("await conn.execute(...): %s", asyncio.run(_await_execute()))


if __name__ == "__main__":
    main()
