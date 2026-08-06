"""PDF 1.7 バイト列の組み立て（標準ライブラリのみ）。

Type0 / CIDFontType2（Identity-H）で TrueType フォントを埋め込み、日本語テキストを描画する。
"""

from __future__ import annotations

import hashlib
import zlib
from dataclasses import dataclass

from truetype import Font, GlyphId, glyph_advance, map_text_to_glyphs

PDF_HEADER = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n"
PDF_TRAILER_FREE_ENTRY = b"0000000000 65535 f \n"
GLYPH_SPACE_UNITS = 1000  # PDF のグリフ空間は em を 1000 分割した単位で表す
ZLIB_LEVEL = 6
BFCHAR_CHUNK_SIZE = 100  # ToUnicode CMap の begincbfchar 1 ブロックあたりの上限
SUBSET_TAG_LENGTH = 6
FONT_DESCRIPTOR_FLAG_SYMBOLIC = 4
STEM_V = 80  # 縦ステムの太さ。ゴシック体の実測値を持たないため代表値を置く
CAP_HEIGHT_RATIO = 0.7

# オブジェクト番号（xref の並びと 1:1 対応させる）
OBJ_CATALOG = 1
OBJ_PAGES = 2
OBJ_PAGE = 3
OBJ_CONTENTS = 4
OBJ_FONT_TYPE0 = 5
OBJ_FONT_CID = 6
OBJ_FONT_DESCRIPTOR = 7
OBJ_FONT_FILE = 8
OBJ_TO_UNICODE = 9


@dataclass(frozen=True, slots=True, kw_only=True)
class PageSpec:
    """1 ページ分の描画指定。"""

    width: float
    height: float
    margin: float
    font_size: float
    leading: float
    lines: tuple[str, ...]


def build_pdf(*, page: PageSpec, font: Font, font_bytes: bytes, subset: bool) -> bytes:
    """描画指定と埋め込みフォントから PDF のバイト列を作る。"""
    glyph_lines = [map_text_to_glyphs(font, line) for line in page.lines]
    used_glyphs = _collect_used_glyphs(page.lines, glyph_lines)
    base_font = _base_font_name(font_bytes, subset=subset)

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        _page_object(page),
        _stream_object(_content_stream(page, glyph_lines)),
        _type0_font_object(base_font),
        _cid_font_object(base_font, font=font, used_glyphs=used_glyphs),
        _font_descriptor_object(base_font, font=font),
        _stream_object(font_bytes, extra=f" /Length1 {len(font_bytes)}"),
        _stream_object(_to_unicode_cmap(used_glyphs)),
    ]
    return _assemble(objects)


def _collect_used_glyphs(
    lines: tuple[str, ...], glyph_lines: list[list[GlyphId]]
) -> dict[GlyphId, str]:
    """描画に使うグリフ ID と、その元になった文字の対応を集める。"""
    used: dict[GlyphId, str] = {}
    for line, glyph_ids in zip(lines, glyph_lines, strict=True):
        for char, glyph_id in zip(line, glyph_ids, strict=True):
            used[glyph_id] = char
    return used


def _page_object(page: PageSpec) -> bytes:
    """ページ辞書を作る。"""
    media_box = f"[0 0 {page.width:.2f} {page.height:.2f}]"
    return (
        f"<< /Type /Page /Parent {OBJ_PAGES} 0 R /MediaBox {media_box} "
        f"/Resources << /Font << /F1 {OBJ_FONT_TYPE0} 0 R >> >> "
        f"/Contents {OBJ_CONTENTS} 0 R >>"
    ).encode("ascii")


def _content_stream(page: PageSpec, glyph_lines: list[list[GlyphId]]) -> bytes:
    """テキスト描画のコンテンツストリームを組み立てる。"""
    baseline_y = page.height - page.margin - page.font_size
    parts = [
        b"BT",
        f"/F1 {page.font_size:.2f} Tf".encode("ascii"),
        f"{page.leading:.2f} TL".encode("ascii"),
        f"1 0 0 1 {page.margin:.2f} {baseline_y:.2f} Tm".encode("ascii"),
    ]
    for glyph_ids in glyph_lines:
        # 空行は Tj を出さず改行だけ進める
        if glyph_ids:
            parts.append(_hex_string(glyph_ids) + b" Tj")
        parts.append(b"T*")
    parts.append(b"ET")
    return b"\n".join(parts)


def _hex_string(glyph_ids: list[GlyphId]) -> bytes:
    """Identity-H でのテキスト実体（グリフ ID の 2 バイト列）を 16 進表記にする。"""
    return b"<" + "".join(f"{glyph_id:04X}" for glyph_id in glyph_ids).encode("ascii") + b">"


def _type0_font_object(base_font: str) -> bytes:
    """合成フォント（Type0）辞書を作る。"""
    return (
        f"<< /Type /Font /Subtype /Type0 /BaseFont /{base_font} /Encoding /Identity-H "
        f"/DescendantFonts [{OBJ_FONT_CID} 0 R] /ToUnicode {OBJ_TO_UNICODE} 0 R >>"
    ).encode("ascii")


def _cid_font_object(base_font: str, *, font: Font, used_glyphs: dict[GlyphId, str]) -> bytes:
    """CIDFontType2 辞書を作る（CID = グリフ ID）。"""
    scale = GLYPH_SPACE_UNITS / font.header.units_per_em
    widths = " ".join(
        f"{glyph_id} [{round(glyph_advance(font, glyph_id) * scale)}]"
        for glyph_id in sorted(used_glyphs)
    )
    return (
        f"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /{base_font} "
        f"/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
        f"/FontDescriptor {OBJ_FONT_DESCRIPTOR} 0 R /DW {GLYPH_SPACE_UNITS} /W [{widths}] "
        f"/CIDToGIDMap /Identity >>"
    ).encode("ascii")


def _font_descriptor_object(base_font: str, *, font: Font) -> bytes:
    """フォント記述子を作る。"""
    scale = GLYPH_SPACE_UNITS / font.header.units_per_em
    bbox = " ".join(str(round(value * scale)) for value in font.header.bbox)
    ascent = round(font.header.ascent * scale)
    descent = round(font.header.descent * scale)
    return (
        f"<< /Type /FontDescriptor /FontName /{base_font} "
        f"/Flags {FONT_DESCRIPTOR_FLAG_SYMBOLIC} /FontBBox [{bbox}] /ItalicAngle 0 "
        f"/Ascent {ascent} /Descent {descent} "
        f"/CapHeight {round(ascent * CAP_HEIGHT_RATIO)} /StemV {STEM_V} "
        f"/FontFile2 {OBJ_FONT_FILE} 0 R >>"
    ).encode("ascii")


def _to_unicode_cmap(used_glyphs: dict[GlyphId, str]) -> bytes:
    """グリフ ID から元の文字を引ける ToUnicode CMap を作る（テキスト抽出用）。"""
    entries = [
        f"<{glyph_id:04X}> <{char.encode('utf-16-be').hex().upper()}>"
        for glyph_id, char in sorted(used_glyphs.items())
    ]
    blocks: list[str] = []
    # bfchar は 1 ブロック 100 件までと決まっているので分割する
    for start in range(0, len(entries), BFCHAR_CHUNK_SIZE):
        chunk = entries[start : start + BFCHAR_CHUNK_SIZE]
        blocks.append(f"{len(chunk)} beginbfchar\n" + "\n".join(chunk) + "\nendbfchar")
    body = "\n".join(blocks)
    return (
        "/CIDInit /ProcSet findresource begin\n"
        "12 dict begin\n"
        "begincmap\n"
        "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
        "/CMapName /Adobe-Identity-UCS def\n"
        "/CMapType 2 def\n"
        "1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n"
        f"{body}\n"
        "endcmap\n"
        "CMapName currentdict /CMap defineresource pop\n"
        "end\nend"
    ).encode("ascii")


def _base_font_name(font_bytes: bytes, *, subset: bool) -> str:
    """BaseFont 名を決める（サブセット時は内容から決まる 6 文字タグを前置する）。"""
    if not subset:
        return "IPAGothic"
    digest = hashlib.sha256(font_bytes).digest()
    # A-Z のみで構成するのが仕様なので 26 文字にマップする
    tag = "".join(chr(ord("A") + byte % 26) for byte in digest[:SUBSET_TAG_LENGTH])
    return f"{tag}+IPAGothic"


def _stream_object(data: bytes, *, extra: str = "") -> bytes:
    """FlateDecode 圧縮したストリームオブジェクトを作る。"""
    compressed = zlib.compress(data, ZLIB_LEVEL)
    header = f"<< /Length {len(compressed)} /Filter /FlateDecode{extra} >>"
    return header.encode("ascii") + b"\nstream\n" + compressed + b"\nendstream"


def _assemble(objects: list[bytes]) -> bytes:
    """オブジェクト列に xref と trailer を付けて PDF 全体にする。"""
    out = bytearray(PDF_HEADER)
    offsets: list[int] = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode("ascii") + body + b"\nendobj\n"

    xref_offset = len(out)
    size = len(objects) + 1  # 0 番の free エントリを含めた総数
    out += f"xref\n0 {size}\n".encode("ascii")
    out += PDF_TRAILER_FREE_ENTRY
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode("ascii")
    out += (
        f"trailer\n<< /Size {size} /Root {OBJ_CATALOG} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
    ).encode("ascii")
    return bytes(out)
