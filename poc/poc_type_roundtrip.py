"""str / int / None が挿入時と同じ型で取り出せるかを実測する。"""
from __future__ import annotations

import logging
import sqlite3

from poc.db import IN_MEMORY_DSN, setup_logger

logger = logging.getLogger(__name__)

CREATE_TYPED_TABLE = "CREATE TABLE typed (text_col TEXT, int_col INTEGER, null_col TEXT)"
CREATE_TEXT_ONLY_TABLE = "CREATE TABLE text_only (value TEXT)"

TEXT_VALUE = "買い物"
INT_VALUE = 42


def _roundtrip_typed() -> None:
    """宣言型がそれぞれの値に合っているカラムで往復させる。"""
    conn = sqlite3.connect(IN_MEMORY_DSN)
    conn.execute(CREATE_TYPED_TABLE)
    conn.execute("INSERT INTO typed VALUES (?, ?, ?)", (TEXT_VALUE, INT_VALUE, None))
    text_col, int_col, null_col = conn.execute(
        "SELECT text_col, int_col, null_col FROM typed"
    ).fetchone()
    logger.info(
        "宣言型に合わせた場合: text=%r(%s) int=%r(%s) null=%r(%s)",
        text_col,
        type(text_col).__name__,
        int_col,
        type(int_col).__name__,
        null_col,
        type(null_col).__name__,
    )
    conn.close()


def _roundtrip_text_affinity() -> None:
    """TEXT 宣言のカラムへ int を入れたときの取り出し型を見る。"""
    conn = sqlite3.connect(IN_MEMORY_DSN)
    conn.execute(CREATE_TEXT_ONLY_TABLE)
    conn.execute("INSERT INTO text_only VALUES (?)", (INT_VALUE,))
    value = conn.execute("SELECT value FROM text_only").fetchone()[0]
    logger.info("TEXT カラムへ int を入れた場合: %r(%s)", value, type(value).__name__)
    conn.close()


def main() -> None:
    """カラムの宣言型ごとに型の往復結果を出力する。"""
    setup_logger()
    _roundtrip_typed()
    _roundtrip_text_affinity()


if __name__ == "__main__":
    main()
