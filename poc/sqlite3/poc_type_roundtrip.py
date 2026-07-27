"""sqlite3 で str / int / None が書き込み時と同じ型で取り出せるかを検証する。"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from _schema import INSERT_TASK, connect_with_schema, find_task

logger = logging.getLogger(__name__)

COLUMNS = ("id", "title", "priority", "due_date")
WRITTEN_ROW: tuple[str, str, int, str | None] = ("t1", "型往復の確認", 3, None)


def run_type_roundtrip(db_path: Path) -> None:
    """書き込んだ値と取り出した値を列ごとに型込みで突き合わせる。"""
    conn = connect_with_schema(db_path)
    conn.execute(INSERT_TASK, WRITTEN_ROW)
    conn.commit()

    read_row = find_task(conn, WRITTEN_ROW[0])
    conn.close()
    if read_row is None:
        raise RuntimeError(f"書き込んだ行が取得できない: id={WRITTEN_ROW[0]}")

    # 列ごとに 書き込み値 と 取得値 を型まで含めて比較する
    for column, written, read in zip(COLUMNS, WRITTEN_ROW, read_row, strict=True):
        matched = type(written) is type(read) and written == read
        logger.info(
            "[型の往復] %-8s 書き込み=%r(%s) 取得=%r(%s) 一致=%s",
            column,
            written,
            type(written).__name__,
            read,
            type(read).__name__,
            matched,
        )


def main() -> None:
    """一時ディレクトリに DB ファイルを作って型の往復を検証する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with tempfile.TemporaryDirectory() as tmp_dir:
        run_type_roundtrip(Path(tmp_dir) / "tasks.db")


if __name__ == "__main__":
    main()
