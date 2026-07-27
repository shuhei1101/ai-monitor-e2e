"""sqlite3 をタスク永続化に使えるかを 4 観点で実測する PoC スクリプト。"""

from __future__ import annotations

import inspect
import logging
import sqlite3
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 一括挿入の検証で投入する行数
BULK_INSERT_ROWS = 1000
# 一括挿入の成功条件（秒）
BULK_INSERT_LIMIT_SECONDS = 1.0

# 検証で使うタスクテーブルの定義
SCHEMA_SQL = """
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    priority INTEGER
)
"""
INSERT_SQL = "INSERT INTO tasks VALUES (?, ?, ?, ?)"


@dataclass(frozen=True, slots=True, kw_only=True)
class VerificationResult:
    """検証観点 1 件分の実測結果。"""

    name: str
    measured: str  # 本文の実測値列にそのまま載せる文字列
    passed: bool


def _connect_with_schema() -> sqlite3.Connection:
    """インメモリ DB を開いてタスクテーブルを作る。"""
    conn = sqlite3.connect(":memory:")
    conn.execute(SCHEMA_SQL)
    return conn


def verify_crud() -> VerificationResult:
    """インメモリ DB で 作成 → 挿入 → 取得 → 更新 → 削除 が一連で通るか確認する。"""
    conn = sqlite3.connect(":memory:")
    completed: list[str] = []

    conn.execute(SCHEMA_SQL)
    completed.append("作成")

    conn.execute(INSERT_SQL, ("t1", "買い物", "牛乳を買う", 1))
    # 挿入した 1 件をそのまま読み戻せるか
    if conn.execute("SELECT title FROM tasks WHERE id = ?", ("t1",)).fetchone() == ("買い物",):
        completed.append("挿入")
        completed.append("取得")

    conn.execute("UPDATE tasks SET title = ? WHERE id = ?", ("買い出し", "t1"))
    # 更新後の値が反映されているか
    if conn.execute("SELECT title FROM tasks WHERE id = ?", ("t1",)).fetchone() == ("買い出し",):
        completed.append("更新")

    conn.execute("DELETE FROM tasks WHERE id = ?", ("t1",))
    # 削除後は 1 件も残っていないか
    if conn.execute("SELECT COUNT(*) FROM tasks").fetchone() == (0,):
        completed.append("削除")

    conn.close()

    return VerificationResult(
        name="インメモリ DB の CRUD",
        measured=" → ".join(completed) + " が成功",
        passed=completed == ["作成", "挿入", "取得", "更新", "削除"],
    )


def verify_bulk_insert() -> VerificationResult:
    """1000 件の一括挿入にかかる時間を測る。"""
    conn = _connect_with_schema()
    rows = [(f"t{i}", f"タスク{i}", f"内容{i}", i % 3) for i in range(BULK_INSERT_ROWS)]

    started = time.perf_counter()
    conn.executemany(INSERT_SQL, rows)
    conn.commit()
    elapsed = time.perf_counter() - started

    inserted = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()

    return VerificationResult(
        name="一括挿入の性能",
        measured=f"{inserted} 件 / {elapsed:.3f} 秒",
        passed=inserted == BULK_INSERT_ROWS and elapsed <= BULK_INSERT_LIMIT_SECONDS,
    )


def verify_type_roundtrip() -> VerificationResult:
    """str / int / None が挿入時と同じ型で取り出せるか確認する。"""
    conn = _connect_with_schema()
    # id=str / title=str / content=None / priority=int の 3 種類を 1 行に混在させる
    inserted = ("t1", "買い物", None, 3)
    conn.execute(INSERT_SQL, inserted)

    fetched = conn.execute(
        "SELECT id, title, content, priority FROM tasks WHERE id = ?", ("t1",)
    ).fetchone()
    conn.close()

    inserted_types = [type(value).__name__ for value in inserted]
    fetched_types = [type(value).__name__ for value in fetched]

    return VerificationResult(
        name="型の往復",
        measured=f"挿入 {inserted_types} → 取得 {fetched_types}",
        passed=inserted_types == fetched_types and inserted == fetched,
    )


def verify_async_query_api() -> VerificationResult:
    """sqlite3 が await 可能なクエリ API を標準で提供するか調べる。"""
    # クエリ発行の入口になるモジュール / 接続 / カーソルを走査対象にする
    targets = {"sqlite3": sqlite3, "sqlite3.Connection": sqlite3.Connection, "sqlite3.Cursor": sqlite3.Cursor}
    coroutine_names: list[str] = []

    for target_name, target in targets.items():
        for attr_name in dir(target):
            # 非公開シンボルは API として数えない
            if attr_name.startswith("_"):
                continue
            if inspect.iscoroutinefunction(getattr(target, attr_name)):
                coroutine_names.append(f"{target_name}.{attr_name}")

    has_async_context = hasattr(sqlite3.Connection, "__aenter__")

    return VerificationResult(
        name="非同期クエリ",
        measured=(
            f"コルーチン関数 {len(coroutine_names)} 件 / "
            f"async context manager {'あり' if has_async_context else 'なし'}"
        ),
        passed=bool(coroutine_names),
    )


def main() -> None:
    """全観点を実行して実測値をログ出力する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    logger.info("SQLite 本体バージョン: %s", sqlite3.sqlite_version)

    for result in (
        verify_crud(),
        verify_bulk_insert(),
        verify_type_roundtrip(),
        verify_async_query_api(),
    ):
        logger.info(
            "[%s] %s | 実測値: %s", "OK" if result.passed else "NG", result.name, result.measured
        )


if __name__ == "__main__":
    main()
