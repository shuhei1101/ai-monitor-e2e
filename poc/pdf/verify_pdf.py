"""生成した PDF の構造を検証する（標準ライブラリのみ）。

xref / trailer の整合、ページツリーの解決、埋め込みフォントのグリフ実体、
ToUnicode 経由のテキスト復元までを機械判定する。
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

import settings
from truetype import GlyphId, read_header, read_loca, read_sfnt_tables

logger = logging.getLogger(__name__)

PDF_HEADER_PREFIX = b"%PDF-1."
XREF_ENTRY_SIZE = 20
GLYPH_HEX_WIDTH = 4  # Identity-H のコードは 2 バイト = 16 進 4 桁


@dataclass(frozen=True, slots=True, kw_only=True)
class PdfDocument:
    """xref を読み終えた PDF。"""

    raw: bytes
    offsets: dict[int, int]  # オブジェクト番号 → ファイル先頭からのバイトオフセット


@dataclass(frozen=True, slots=True, kw_only=True)
class CheckResult:
    """検証項目 1 件の結果。"""

    name: str
    passed: bool
    detail: str


def verify(path: Path, expected_lines: tuple[str, ...]) -> list[CheckResult]:
    """PDF を検証して項目ごとの結果を返す。"""
    raw = path.read_bytes()
    document = PdfDocument(raw=raw, offsets=_read_xref(raw))
    page_body = _page_object(document)
    to_unicode = _read_to_unicode(document)
    extracted = _extract_lines(document, page_body=page_body, to_unicode=to_unicode)

    return [
        _check_header(raw),
        _check_xref(document),
        _check_page_tree(document, page_body=page_body),
        _check_text(extracted, expected_lines=expected_lines),
        _check_embedded_font(document, to_unicode=to_unicode),
    ]


def _check_header(raw: bytes) -> CheckResult:
    """PDF ヘッダと %%EOF の有無を見る。"""
    has_header = raw.startswith(PDF_HEADER_PREFIX)
    has_eof = raw.rstrip().endswith(b"%%EOF")
    return CheckResult(
        name="ヘッダ / EOF",
        passed=has_header and has_eof,
        detail=f"{raw[:8].decode('ascii', 'replace')} … %%EOF={'あり' if has_eof else 'なし'}",
    )


def _check_xref(document: PdfDocument) -> CheckResult:
    """xref の各オフセットが実際のオブジェクト先頭を指しているかを見る。"""
    broken = [
        number
        for number, offset in document.offsets.items()
        if not document.raw.startswith(f"{number} 0 obj".encode("ascii"), offset)
    ]
    return CheckResult(
        name="xref オフセット整合",
        passed=not broken,
        detail=f"{len(document.offsets)} 件中 不整合 {len(broken)} 件",
    )


def _check_page_tree(document: PdfDocument, *, page_body: bytes) -> CheckResult:
    """trailer から Catalog → Pages → Page まで辿れるかを見る。"""
    media_box = re.search(rb"/MediaBox\s*\[([^\]]*)\]", page_body)
    has_font = re.search(rb"/Font\s*<<", page_body) is not None
    resolved = b"/Type /Page" in page_body and media_box is not None and has_font
    box = media_box.group(1).decode("ascii").strip() if media_box else "なし"
    return CheckResult(
        name="ページツリー解決",
        passed=resolved,
        detail=f"Root → Pages → Page を解決 / MediaBox=[{box}]",
    )


def _check_text(extracted: list[str], *, expected_lines: tuple[str, ...]) -> CheckResult:
    """ToUnicode 経由で復元した本文が元のテキストと一致するかを見る。"""
    expected = [line for line in expected_lines if line]  # 空行は Tj を出していない
    return CheckResult(
        name="本文テキスト復元",
        passed=extracted == expected,
        detail=f"{len(extracted)}/{len(expected)} 行一致（先頭: {extracted[0] if extracted else ''}）",
    )


def _check_embedded_font(document: PdfDocument, *, to_unicode: dict[GlyphId, str]) -> CheckResult:
    """埋め込みフォントを再パースし、使用グリフの輪郭が残っているかを見る。"""
    descendant = _object_body(document, _reference(_font_object(document), "DescendantFonts"))
    descriptor = _object_body(document, _reference(descendant, "FontDescriptor"))
    font_file_body = _object_body(document, _reference(descriptor, "FontFile2"))
    font_bytes = _stream_bytes(font_file_body)

    tables = read_sfnt_tables(font_bytes)
    header = read_header(tables)
    loca = read_loca(tables, header)
    # 空白文字は輪郭を持たないのが正しいので、実体の有無を見る対象から外す
    drawable = [glyph_id for glyph_id, char in to_unicode.items() if not char.isspace()]
    empty = [glyph_id for glyph_id in drawable if loca[glyph_id + 1] <= loca[glyph_id]]
    declared_length = int(re.search(rb"/Length1\s+(\d+)", font_file_body).group(1))

    return CheckResult(
        name="埋め込みフォント",
        passed=not empty and declared_length == len(font_bytes),
        detail=(
            f"{len(font_bytes) / 1024:.1f} KiB / 使用 {len(drawable)} グリフ中 "
            f"輪郭なし {len(empty)} 件 / Length1 一致={declared_length == len(font_bytes)}"
        ),
    )


def _read_xref(raw: bytes) -> dict[int, int]:
    """末尾の startxref から xref テーブルを読む（単一サブセクション前提）。"""
    marker = raw.rfind(b"startxref")
    if marker < 0:
        raise ValueError("startxref が見つかりません")
    xref_offset = int(raw[marker + len("startxref") :].split()[0])

    section = raw[xref_offset:]
    header = re.match(rb"xref\s+(\d+)\s+(\d+)\s", section)
    if header is None:
        raise ValueError(f"xref テーブルがありません: offset={xref_offset}")
    first_number, count = int(header.group(1)), int(header.group(2))

    offsets: dict[int, int] = {}
    for index in range(count):
        start = header.end() + XREF_ENTRY_SIZE * index
        offset, _generation, kind = section[start : start + XREF_ENTRY_SIZE].split()
        # f エントリ（未使用オブジェクト）は実体を持たないので対象外
        if kind == b"n":
            offsets[first_number + index] = int(offset)
    return offsets


def _object_body(document: PdfDocument, number: int) -> bytes:
    """オブジェクト番号から `N 0 obj` … `endobj` の中身を取り出す。"""
    offset = document.offsets[number]
    prefix = f"{number} 0 obj".encode("ascii")
    if not document.raw.startswith(prefix, offset):
        raise ValueError(f"オブジェクト {number} が xref の位置にありません")
    end = document.raw.index(b"endobj", offset)
    return document.raw[offset + len(prefix) : end].strip()


def _stream_bytes(body: bytes) -> bytes:
    """ストリームオブジェクトの中身を /Length 分だけ切り出して展開する。"""
    length = int(re.search(rb"/Length\s+(\d+)", body).group(1))
    start = body.index(b"stream") + len(b"stream") + 1  # キーワード直後の改行を跨ぐ
    data = body[start : start + length]
    if b"/FlateDecode" in body[:start]:
        return zlib.decompress(data)
    return data


def _reference(body: bytes, key: str) -> int:
    """辞書から `/Key N 0 R` 形式の参照先オブジェクト番号を取る。"""
    match = re.search(rf"/{re.escape(key)}\s*\[?\s*(\d+)\s+0\s+R".encode("ascii"), body)
    if match is None:
        raise ValueError(f"参照 /{key} が見つかりません")
    return int(match.group(1))


def _page_object(document: PdfDocument) -> bytes:
    """trailer から辿って最初のページオブジェクトを返す。"""
    trailer = document.raw[document.raw.rfind(b"trailer") :]
    catalog = _object_body(document, _reference(trailer, "Root"))
    pages = _object_body(document, _reference(catalog, "Pages"))
    return _object_body(document, _reference(pages, "Kids"))


def _font_object(document: PdfDocument) -> bytes:
    """ページのリソースから合成フォント（Type0）オブジェクトを返す。"""
    page_body = _page_object(document)
    return _object_body(document, _reference(page_body, "F1"))


def _read_to_unicode(document: PdfDocument) -> dict[GlyphId, str]:
    """ToUnicode CMap を読み、グリフ ID → 文字の対応にする。"""
    cmap_body = _object_body(document, _reference(_font_object(document), "ToUnicode"))
    cmap_text = _stream_bytes(cmap_body).decode("ascii")
    mapping: dict[GlyphId, str] = {}
    # codespacerange と混ざらないよう bfchar ブロックの中だけを読む
    for block in re.findall(r"beginbfchar(.*?)endbfchar", cmap_text, re.DOTALL):
        for source, target in re.findall(r"<([0-9A-F]+)>\s*<([0-9A-F]+)>", block):
            mapping[int(source, 16)] = bytes.fromhex(target).decode("utf-16-be")
    return mapping


def _extract_lines(
    document: PdfDocument, *, page_body: bytes, to_unicode: dict[GlyphId, str]
) -> list[str]:
    """コンテンツストリームの Tj を ToUnicode で文字列に戻す。"""
    content = _stream_bytes(_object_body(document, _reference(page_body, "Contents")))
    lines: list[str] = []
    for hex_text in re.findall(rb"<([0-9A-F]+)>\s*Tj", content):
        codes = hex_text.decode("ascii")
        glyph_ids = [
            int(codes[position : position + GLYPH_HEX_WIDTH], 16)
            for position in range(0, len(codes), GLYPH_HEX_WIDTH)
        ]
        lines.append("".join(to_unicode[glyph_id] for glyph_id in glyph_ids))
    return lines


def main() -> int:
    """CLI エントリポイント。"""
    parser = argparse.ArgumentParser(description="生成した PDF の構造を検証する")
    parser.add_argument("--pdf", type=Path, default=settings.OUTPUT_PATH, help="検証する PDF")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    results = verify(args.pdf, settings.SAMPLE_LINES)
    for result in results:
        logger.info("%s %s: %s", "OK  " if result.passed else "NG  ", result.name, result.detail)

    failed = [result for result in results if not result.passed]
    logger.info("検証結果: %d/%d 項目 pass", len(results) - len(failed), len(results))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
