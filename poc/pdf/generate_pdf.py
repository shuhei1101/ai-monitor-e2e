"""標準ライブラリのみで日本語 PDF を生成する PoC のエントリポイント。"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import settings
from pdf_writer import PageSpec, build_pdf
from truetype import map_text_to_glyphs, read_font, subset_font

logger = logging.getLogger(__name__)

BYTES_PER_KIB = 1024


def generate(*, font_path: Path, output_path: Path, subset: bool) -> Path:
    """サンプル本文の PDF を生成して出力先パスを返す。"""
    started = time.perf_counter()
    font = read_font(font_path)
    logger.info(
        "フォント読込: %s (%.1f KiB, グリフ数 %d, unitsPerEm %d)",
        font_path,
        len(font.raw) / BYTES_PER_KIB,
        font.header.num_glyphs,
        font.header.units_per_em,
    )

    # 埋め込むフォント実体を決める（サブセット時は使用グリフだけを残す）
    if subset:
        used_glyphs = {
            glyph_id
            for line in settings.SAMPLE_LINES
            for glyph_id in map_text_to_glyphs(font, line)
        }
        font_bytes = subset_font(font, used_glyphs)
        logger.info(
            "サブセット化: %d グリフ → %.1f KiB", len(used_glyphs), len(font_bytes) / BYTES_PER_KIB
        )
    else:
        font_bytes = font.raw
        logger.info("サブセット化なし: %.1f KiB を丸ごと埋め込む", len(font_bytes) / BYTES_PER_KIB)

    page = PageSpec(
        width=settings.PAGE_WIDTH_PT,
        height=settings.PAGE_HEIGHT_PT,
        margin=settings.PAGE_MARGIN_PT,
        font_size=settings.FONT_SIZE_PT,
        leading=settings.LINE_LEADING_PT,
        lines=settings.SAMPLE_LINES,
    )
    pdf_bytes = build_pdf(page=page, font=font, font_bytes=font_bytes, subset=subset)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf_bytes)
    elapsed = time.perf_counter() - started
    logger.info(
        "生成完了: %s (%.1f KiB, %.3f 秒)", output_path, len(pdf_bytes) / BYTES_PER_KIB, elapsed
    )
    return output_path


def main() -> int:
    """CLI エントリポイント。"""
    parser = argparse.ArgumentParser(description="標準ライブラリのみで日本語 PDF を生成する")
    parser.add_argument("--font", type=Path, default=settings.FONT_PATH, help="埋め込むフォント")
    parser.add_argument("--out", type=Path, default=settings.OUTPUT_PATH, help="出力先 PDF")
    parser.add_argument(
        "--no-subset", action="store_true", help="サブセット化せずフォントを丸ごと埋め込む"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    generate(font_path=args.font, output_path=args.out, subset=not args.no_subset)
    return 0


if __name__ == "__main__":
    sys.exit(main())
