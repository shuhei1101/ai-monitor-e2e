"""pathlib + tempfile による一時ファイルの往復が標準ライブラリのみで成立するかを検証する。"""

from __future__ import annotations

import logging
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

ENCODING = "utf-8"
ASCII_PAYLOAD = "poc-tempfile-roundtrip"
UTF8_PAYLOAD = "一時ファイルの往復検証（日本語・絵文字🗂️を含む）"
ASCII_FILE_NAME = "ascii_payload.txt"
UTF8_FILE_NAME = "utf8_payload.txt"


@dataclass(frozen=True, slots=True, kw_only=True)
class RoundTripResult:
    """1 ケース分の往復検証の実測値。"""

    case: str
    written_chars: int
    expected_chars: int
    restored_matches: bool
    file_size_bytes: int


def run_round_trip(*, directory: Path, file_name: str, payload: str, case: str) -> RoundTripResult:
    """一時ディレクトリ配下へ payload を書き込み、読み戻して一致を確認する。"""
    target = directory / file_name
    # write_text は書き込んだ文字数を返す（バイト数ではない）
    written_chars = target.write_text(payload, encoding=ENCODING)
    restored = target.read_text(encoding=ENCODING)
    return RoundTripResult(
        case=case,
        written_chars=written_chars,
        expected_chars=len(payload),
        restored_matches=restored == payload,
        file_size_bytes=target.stat().st_size,
    )


def main() -> int:
    """検証を実行し、実測値を出力する。"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    with tempfile.TemporaryDirectory() as raw_dir:
        directory = Path(raw_dir)
        logger.info("一時ディレクトリ: %s", directory)
        results = [
            run_round_trip(
                directory=directory,
                file_name=ASCII_FILE_NAME,
                payload=ASCII_PAYLOAD,
                case="ASCII",
            ),
            run_round_trip(
                directory=directory,
                file_name=UTF8_FILE_NAME,
                payload=UTF8_PAYLOAD,
                case="非 ASCII（日本語 + 絵文字）",
            ),
        ]

    # with を抜けた後にディレクトリごと消えているかを確認する（後始末の成功条件）
    cleaned_up = not directory.exists()

    for result in results:
        logger.info(
            "%s: 書き込み文字数=%d 期待文字数=%d 復元一致=%s ファイルサイズ=%dバイト",
            result.case,
            result.written_chars,
            result.expected_chars,
            result.restored_matches,
            result.file_size_bytes,
        )
    logger.info("スコープ退出後の一時ディレクトリ削除: %s", cleaned_up)
    logger.info("Python: %s", sys.version.split()[0])

    all_passed = cleaned_up and all(
        r.restored_matches and r.written_chars == r.expected_chars for r in results
    )
    logger.info("総合判定: %s", "成立" if all_passed else "不成立")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
