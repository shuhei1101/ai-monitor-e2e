"""検証スクリプト共通のヘルパー。"""

from __future__ import annotations


def mark(ok: bool) -> str:
    """判定結果をログ用の文言に変換する。"""
    return "成功" if ok else "失敗"
