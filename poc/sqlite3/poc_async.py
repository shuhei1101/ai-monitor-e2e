"""sqlite3 が await 可能なクエリ API を標準で提供するかを確認する PoC。"""

from __future__ import annotations

import asyncio
import inspect
import logging
import sqlite3

logger = logging.getLogger(__name__)

# クエリ発行に使う主要 API。この中にコルーチン関数があれば「標準で await 可能」とみなす
QUERY_API_NAMES = ("connect", "execute", "executemany", "executescript", "commit", "fetchone", "fetchall")


def find_coroutine_query_apis() -> list[str]:
    """主要クエリ API のうちコルーチン関数として定義されているものの名前を返す。"""
    found: list[str] = []
    for holder in (sqlite3, sqlite3.Connection, sqlite3.Cursor):
        for name in QUERY_API_NAMES:
            attr = getattr(holder, name, None)
            if attr is None:
                continue
            if inspect.iscoroutinefunction(attr):
                found.append(f"{holder.__name__}.{name}")
    return found


def find_async_protocol_members() -> list[str]:
    """接続 / カーソルが実装している非同期プロトコル（async with / async for）の名前を返す。"""
    return [
        f"{holder.__name__}.{name}"
        for holder in (sqlite3.Connection, sqlite3.Cursor)
        for name in ("__aenter__", "__aexit__", "__aiter__", "__anext__")
        if hasattr(holder, name)
    ]


async def try_await_execute() -> str:
    """execute() の戻り値を await した結果を、成功可否が分かる文字列で返す。"""
    conn = sqlite3.connect(":memory:")
    returned = conn.execute("SELECT 1")
    try:
        await returned  # type: ignore[misc]  # await 不可であることの実測が目的
    except TypeError as e:
        return f"await 不可（{type(returned).__name__} を await して TypeError: {e}）"
    finally:
        conn.close()
    return f"await 可（戻り値: {type(returned).__name__}）"


async def main() -> None:
    """コルーチン API の有無・非同期プロトコルの有無・実際の await 結果を出力する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("[ASYNC] コルーチン関数として定義されたクエリ API: %s", find_coroutine_query_apis())
    logger.info("[ASYNC] 実装済みの非同期プロトコル: %s", find_async_protocol_members())
    logger.info("[ASYNC] execute() の戻り値を await: %s", await try_await_execute())


if __name__ == "__main__":
    asyncio.run(main())
