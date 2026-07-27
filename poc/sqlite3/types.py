"""sqlite3 PoC で扱う DTO と型エイリアス。"""

from __future__ import annotations

from dataclasses import dataclass

type TaskId = str


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """検証対象のタスク 1 件。"""

    id: TaskId
    title: str
    priority: int
    # 未入力を許すため None を取りうる（SQLite 側は NULL）
    memo: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class BulkWriteConfig:
    """一括書き込み検証のパラメータ。"""

    record_count: int
    time_limit_sec: float


@dataclass(frozen=True, slots=True, kw_only=True)
class PocConfig:
    """PoC 全体の検証パラメータ。"""

    db_filename: str
    bulk_write: BulkWriteConfig
