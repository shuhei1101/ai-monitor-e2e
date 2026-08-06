"""TrueType フォントの解析とサブセット化。

PDF への埋め込みに必要な範囲（メトリクス / cmap / glyf / loca）だけを扱う。
"""

from __future__ import annotations

import struct
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

type GlyphId = int

SFNT_VERSION_TRUETYPE = 0x00010000
TABLE_DIRECTORY_OFFSET = 12
TABLE_RECORD_SIZE = 16
TABLE_ALIGNMENT = 4
CHECKSUM_MODULO = 1 << 32
HEAD_CHECKSUM_MAGIC = 0xB1B0AFBA
HEAD_CHECKSUM_ADJUSTMENT_OFFSET = 8
HEAD_UNITS_PER_EM_OFFSET = 18
HEAD_BBOX_OFFSET = 36
HEAD_INDEX_TO_LOC_FORMAT_OFFSET = 50
HHEA_ASCENDER_OFFSET = 4
HHEA_NUM_H_METRICS_OFFSET = 34
MAXP_NUM_GLYPHS_OFFSET = 4
HMTX_ENTRY_SIZE = 4
LOC_FORMAT_LONG = 1
NOTDEF_GLYPH_ID = 0

# cmap サブテーブルの優先順位（値が大きいほど優先して採用する）
CMAP_ENCODING_PRIORITY = {
    (3, 10): 3,  # Windows / UCS-4
    (3, 1): 2,  # Windows / BMP
    (0, 4): 1,  # Unicode / BMP 超えを含む
    (0, 3): 1,  # Unicode / BMP
}
CMAP_FORMAT_SEGMENTED = 4
CMAP_FORMAT_MANY_TO_ONE = 12
CMAP_LAST_BMP_CODE = 0xFFFF

# 複合グリフのフラグ（構成グリフを辿るために必要な分だけ定義する）
COMPOSITE_ARGS_ARE_WORDS = 0x0001
COMPOSITE_HAS_SCALE = 0x0008
COMPOSITE_MORE_COMPONENTS = 0x0020
COMPOSITE_HAS_XY_SCALE = 0x0040
COMPOSITE_HAS_2X2 = 0x0080
COMPOSITE_HEADER_SIZE = 10

# サブセットに残すテーブル
# cmap / post / name / GSUB は CIDFontType2 + CIDToGIDMap=Identity のもとでは参照されない
SUBSET_TABLE_TAGS = ("OS/2", "cvt ", "fpgm", "glyf", "head", "hhea", "hmtx", "loca", "maxp", "prep")


@dataclass(frozen=True, slots=True, kw_only=True)
class FontHeader:
    """head / hhea / maxp から読んだフォント全体のメトリクス。"""

    units_per_em: int
    index_to_loc_format: int  # 0=loca が 2 バイト / 1=4 バイト
    bbox: tuple[int, int, int, int]
    ascent: int
    descent: int
    num_glyphs: int
    num_h_metrics: int  # hmtx で advanceWidth を持つ先頭グリフ数


@dataclass(frozen=True, slots=True, kw_only=True)
class Font:
    """解析済みの TrueType フォント。"""

    path: Path
    raw: bytes
    tables: dict[str, bytes]
    header: FontHeader
    cmap: dict[int, GlyphId]  # Unicode コードポイント → グリフ ID


def read_font(path: Path) -> Font:
    """TrueType フォントを読み込んで解析済みの Font にする。"""
    raw = path.read_bytes()
    tables = read_sfnt_tables(raw)
    return Font(
        path=path,
        raw=raw,
        tables=tables,
        header=read_header(tables),
        cmap=_read_cmap(tables["cmap"]),
    )


def read_sfnt_tables(raw: bytes) -> dict[str, bytes]:
    """sfnt のテーブルディレクトリを読み、タグ → バイト列の辞書にする。"""
    sfnt_version, num_tables = struct.unpack_from(">IH", raw, 0)
    if sfnt_version != SFNT_VERSION_TRUETYPE:
        raise ValueError(f"TrueType グリフを持つフォントではありません: sfnt={sfnt_version:#x}")
    tables: dict[str, bytes] = {}
    for index in range(num_tables):
        record = TABLE_DIRECTORY_OFFSET + TABLE_RECORD_SIZE * index
        tag = raw[record : record + 4].decode("ascii")
        offset, length = struct.unpack_from(">II", raw, record + 8)
        tables[tag] = raw[offset : offset + length]
    return tables


def read_header(tables: dict[str, bytes]) -> FontHeader:
    """head / hhea / maxp からメトリクスを読む。"""
    head = tables["head"]
    hhea = tables["hhea"]
    ascent, descent = struct.unpack_from(">hh", hhea, HHEA_ASCENDER_OFFSET)
    return FontHeader(
        units_per_em=struct.unpack_from(">H", head, HEAD_UNITS_PER_EM_OFFSET)[0],
        index_to_loc_format=struct.unpack_from(">h", head, HEAD_INDEX_TO_LOC_FORMAT_OFFSET)[0],
        bbox=struct.unpack_from(">hhhh", head, HEAD_BBOX_OFFSET),
        ascent=ascent,
        descent=descent,
        num_glyphs=struct.unpack_from(">H", tables["maxp"], MAXP_NUM_GLYPHS_OFFSET)[0],
        num_h_metrics=struct.unpack_from(">H", hhea, HHEA_NUM_H_METRICS_OFFSET)[0],
    )


def read_loca(tables: dict[str, bytes], header: FontHeader) -> list[int]:
    """loca テーブルを glyf 内のバイトオフセット列として読む。"""
    loca = tables["loca"]
    count = header.num_glyphs + 1
    if header.index_to_loc_format == LOC_FORMAT_LONG:
        return list(struct.unpack_from(f">{count}I", loca, 0))
    # short 形式は実オフセットの 1/2 が格納されている
    return [value * 2 for value in struct.unpack_from(f">{count}H", loca, 0)]


def map_text_to_glyphs(font: Font, text: str) -> list[GlyphId]:
    """文字列をグリフ ID 列に変換する（フォントに無い文字は例外）。"""
    glyph_ids: list[GlyphId] = []
    for char in text:
        glyph_id = font.cmap.get(ord(char))
        if glyph_id is None:
            raise ValueError(f"フォントに含まれない文字です: {char!r} (U+{ord(char):04X})")
        glyph_ids.append(glyph_id)
    return glyph_ids


def glyph_advance(font: Font, glyph_id: GlyphId) -> int:
    """グリフの送り幅をフォント単位で返す。"""
    # hmtx の後半は advanceWidth を省略し、末尾エントリの値を共有する
    index = min(glyph_id, font.header.num_h_metrics - 1)
    return struct.unpack_from(">H", font.tables["hmtx"], index * HMTX_ENTRY_SIZE)[0]


def subset_font(font: Font, glyph_ids: Iterable[GlyphId]) -> bytes:
    """指定グリフだけを残した sfnt バイト列を返す（グリフ ID の採番は元のまま）。"""
    loca = read_loca(font.tables, font.header)
    glyf = font.tables["glyf"]
    keep = _expand_composites(glyph_ids, loca=loca, glyf=glyf)

    # glyf を詰め直し、loca を新しいオフセットで作り直す
    new_glyf = bytearray()
    new_loca: list[int] = []
    for glyph_id in range(font.header.num_glyphs):
        new_loca.append(len(new_glyf))
        if glyph_id not in keep:
            continue  # 残さないグリフは長さ 0（loca の隣接オフセットが同値になる）
        data = glyf[loca[glyph_id] : loca[glyph_id + 1]]
        new_glyf += data
        new_glyf += b"\x00" * (-len(data) % TABLE_ALIGNMENT)
    new_loca.append(len(new_glyf))

    # loca を long 形式に統一するので head の indexToLocFormat も合わせる
    head = bytearray(font.tables["head"])
    struct.pack_into(">h", head, HEAD_INDEX_TO_LOC_FORMAT_OFFSET, LOC_FORMAT_LONG)

    tables = {tag: font.tables[tag] for tag in SUBSET_TABLE_TAGS if tag in font.tables}
    tables["head"] = bytes(head)
    tables["glyf"] = bytes(new_glyf)
    tables["loca"] = struct.pack(f">{len(new_loca)}I", *new_loca)
    return build_sfnt(tables)


def build_sfnt(tables: dict[str, bytes]) -> bytes:
    """テーブル群からチェックサム込みの sfnt バイト列を組み立てる。"""
    tags = sorted(tables)
    num_tables = len(tags)
    # テーブルディレクトリの二分探索用パラメータ（仕様で 2 の冪から算出する）
    highest_power_of_two = 1 << (num_tables.bit_length() - 1)
    search_range = highest_power_of_two * TABLE_RECORD_SIZE
    entry_selector = num_tables.bit_length() - 1
    range_shift = num_tables * TABLE_RECORD_SIZE - search_range

    header = struct.pack(
        ">IHHHH", SFNT_VERSION_TRUETYPE, num_tables, search_range, entry_selector, range_shift
    )
    body_offset = TABLE_DIRECTORY_OFFSET + TABLE_RECORD_SIZE * num_tables
    records = bytearray()
    body = bytearray()
    head_offset = 0
    for tag in tags:
        data = tables[tag]
        offset = body_offset + len(body)
        if tag == "head":
            head_offset = offset  # checkSumAdjustment を後から書き込むため位置を控える
        records += tag.encode("ascii")
        records += struct.pack(">III", _table_checksum(data), offset, len(data))
        body += data + b"\x00" * (-len(data) % TABLE_ALIGNMENT)

    font_bytes = bytearray(header + records + body)
    # head の checkSumAdjustment はフォント全体のチェックサムから決まるので最後に埋める
    struct.pack_into(">I", font_bytes, head_offset + HEAD_CHECKSUM_ADJUSTMENT_OFFSET, 0)
    adjustment = (HEAD_CHECKSUM_MAGIC - _table_checksum(bytes(font_bytes))) % CHECKSUM_MODULO
    struct.pack_into(">I", font_bytes, head_offset + HEAD_CHECKSUM_ADJUSTMENT_OFFSET, adjustment)
    return bytes(font_bytes)


def _read_cmap(table: bytes) -> dict[int, GlyphId]:
    """cmap から Unicode → グリフ ID の対応表を作る。"""
    num_subtables = struct.unpack_from(">H", table, 2)[0]
    best_offset = 0
    best_priority = 0
    for index in range(num_subtables):
        platform_id, encoding_id, offset = struct.unpack_from(">HHI", table, 4 + 8 * index)
        priority = CMAP_ENCODING_PRIORITY.get((platform_id, encoding_id), 0)
        if priority > best_priority:
            best_priority, best_offset = priority, offset
    if best_priority == 0:
        raise ValueError("Unicode を引ける cmap サブテーブルがありません")

    subtable = table[best_offset:]
    subtable_format = struct.unpack_from(">H", subtable, 0)[0]
    if subtable_format == CMAP_FORMAT_SEGMENTED:
        return _read_cmap_format4(subtable)
    if subtable_format == CMAP_FORMAT_MANY_TO_ONE:
        return _read_cmap_format12(subtable)
    raise ValueError(f"未対応の cmap format です: {subtable_format}")


def _read_cmap_format4(subtable: bytes) -> dict[int, GlyphId]:
    """format 4（BMP のセグメント方式）を展開する。"""
    segment_count = struct.unpack_from(">H", subtable, 6)[0] // 2
    ends = struct.unpack_from(f">{segment_count}H", subtable, 14)
    starts_offset = 14 + segment_count * 2 + 2  # reservedPad の 2 バイトを跨ぐ
    starts = struct.unpack_from(f">{segment_count}H", subtable, starts_offset)
    deltas_offset = starts_offset + segment_count * 2
    deltas = struct.unpack_from(f">{segment_count}h", subtable, deltas_offset)
    range_offsets_position = deltas_offset + segment_count * 2
    range_offsets = struct.unpack_from(f">{segment_count}H", subtable, range_offsets_position)

    mapping: dict[int, GlyphId] = {}
    for segment in range(segment_count):
        for code in range(starts[segment], ends[segment] + 1):
            if code == CMAP_LAST_BMP_CODE:
                continue  # 終端マーカーなので実文字として扱わない
            if range_offsets[segment] == 0:
                # idDelta だけでグリフ ID が決まる区間
                glyph_id = (code + deltas[segment]) & 0xFFFF
            else:
                # glyphIdArray を idRangeOffset 経由で引く区間
                position = (
                    range_offsets_position
                    + segment * 2
                    + range_offsets[segment]
                    + (code - starts[segment]) * 2
                )
                glyph_id = struct.unpack_from(">H", subtable, position)[0]
                if glyph_id != NOTDEF_GLYPH_ID:
                    glyph_id = (glyph_id + deltas[segment]) & 0xFFFF
            if glyph_id != NOTDEF_GLYPH_ID:
                mapping[code] = glyph_id
    return mapping


def _read_cmap_format12(subtable: bytes) -> dict[int, GlyphId]:
    """format 12（BMP 超えを含むグループ方式）を展開する。"""
    num_groups = struct.unpack_from(">I", subtable, 12)[0]
    mapping: dict[int, GlyphId] = {}
    for index in range(num_groups):
        start_code, end_code, start_glyph_id = struct.unpack_from(">III", subtable, 16 + 12 * index)
        for offset in range(end_code - start_code + 1):
            mapping[start_code + offset] = start_glyph_id + offset
    return mapping


def _expand_composites(
    glyph_ids: Iterable[GlyphId], *, loca: list[int], glyf: bytes
) -> set[GlyphId]:
    """指定グリフに複合グリフの構成グリフと .notdef を加えた集合を返す。"""
    pending = [*glyph_ids, NOTDEF_GLYPH_ID]
    keep: set[GlyphId] = set()
    while pending:
        glyph_id = pending.pop()
        if glyph_id in keep:
            continue
        keep.add(glyph_id)
        # 複合グリフなら構成グリフも残さないと描画できない
        pending.extend(_component_glyph_ids(glyf[loca[glyph_id] : loca[glyph_id + 1]]))
    return keep


def _component_glyph_ids(data: bytes) -> list[GlyphId]:
    """複合グリフが参照する構成グリフ ID を列挙する（単純グリフなら空）。"""
    if not data:
        return []
    if struct.unpack_from(">h", data, 0)[0] >= 0:
        return []  # numberOfContours が非負なら単純グリフ

    components: list[GlyphId] = []
    offset = COMPOSITE_HEADER_SIZE
    while True:
        flags, glyph_id = struct.unpack_from(">HH", data, offset)
        components.append(glyph_id)
        offset += 4
        # 引数は 8bit / 16bit の可変長
        offset += 4 if flags & COMPOSITE_ARGS_ARE_WORDS else 2
        # 変形行列の有無で後続バイト数が変わる
        if flags & COMPOSITE_HAS_SCALE:
            offset += 2
        elif flags & COMPOSITE_HAS_XY_SCALE:
            offset += 4
        elif flags & COMPOSITE_HAS_2X2:
            offset += 8
        if not flags & COMPOSITE_MORE_COMPONENTS:
            return components


def _table_checksum(data: bytes) -> int:
    """sfnt テーブルのチェックサム（4 バイト単位の総和）を求める。"""
    padded = data + b"\x00" * (-len(data) % TABLE_ALIGNMENT)
    return sum(struct.unpack(f">{len(padded) // 4}I", padded)) % CHECKSUM_MODULO
