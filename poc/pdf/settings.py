"""PoC の入出力パスと描画パラメータ。

外部依存ゼロが検証対象のため YAML パーサ（PyYAML）を使えず、設定値は Python モジュールに置く。
"""

from __future__ import annotations

from pathlib import Path

FONT_PATH = Path("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf")
OUTPUT_DIR = Path(__file__).parent / "out"
OUTPUT_PATH = OUTPUT_DIR / "sample.pdf"

# A4 縦（1pt = 1/72 inch）
PAGE_WIDTH_PT = 595.28
PAGE_HEIGHT_PT = 841.89
PAGE_MARGIN_PT = 56.7  # 約 2cm
FONT_SIZE_PT = 13.0
LINE_LEADING_PT = 21.0

# 生成 PDF に描画する本文（日本語・記号・ASCII を混在させて埋め込みの成否を見る）
SAMPLE_LINES = (
    "標準ライブラリのみによる PDF 生成 PoC",
    "",
    "このファイルは Python 3.12 の標準ライブラリだけで生成しています。",
    "reportlab などの外部パッケージは一切使用していません。",
    "",
    "濁点・半濁点: がぎぐげご / ぱぴぷぺぽ",
    "漢字: 一時ファイル生成機構 の実現可能性検証",
    "記号: 〜 「」 『』 ％ ＆ ＠ ・ ／",
    "ASCII: ABCDEFabcdef 0123456789",
    "",
    "epic #2901 / PoC PR #2902",
)
