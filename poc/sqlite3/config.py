"""検証パラメータ（config.yaml）の読み込み。"""

from __future__ import annotations

from pathlib import Path

import yaml

from poc.sqlite3.types import BulkWriteConfig, PocConfig

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> PocConfig:
    """config.yaml を読んで検証パラメータを返す。"""
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return PocConfig(
        db_filename=raw["db_filename"],
        bulk_write=BulkWriteConfig(
            record_count=raw["bulk_write"]["record_count"],
            time_limit_sec=raw["bulk_write"]["time_limit_sec"],
        ),
    )
