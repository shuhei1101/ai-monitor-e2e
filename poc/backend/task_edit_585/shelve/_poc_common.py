"""shelve PoC の各検証スクリプトで共有する型とヘルパー。"""

from __future__ import annotations

import dbm
import logging
from pathlib import Path
from typing import TypedDict

type TaskId = str


class Task(TypedDict):
    """タスク編集バックエンドで永続化するタスク 1 件。"""

    id: TaskId
    title: str
    priority: int
    memo: str | None


def configure_logging() -> logging.Logger:
    """PoC スクリプト用のロガーを標準出力向けに設定する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    return logging.getLogger("shelve_poc")


def store_path(base_dir: Path, stem: str) -> str:
    """shelve に渡す拡張子なしのストアパスを返す。"""
    return str(base_dir / stem)


def describe_store(path: str) -> str:
    """shelve が実際に使った dbm 実装名と、生成された実ファイル名を返す。"""
    which = dbm.whichdb(path)
    base = Path(path)
    # 実ファイルは dbm 実装ごとに拡張子が変わるため、同名で始まるファイルを列挙する
    generated = sorted(p.name for p in base.parent.iterdir() if p.name.startswith(base.name))
    return f"dbm 実装={which} / 生成ファイル={generated}"
