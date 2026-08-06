"""PoC のスクリプト群が標準ライブラリだけで動いているかを検査する。

import 文の静的走査と、実際に PDF を生成した後の sys.modules 検査の 2 面から見る。
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import subprocess
import sys
from pathlib import Path

import generate_pdf
import settings

logger = logging.getLogger(__name__)


def collect_imported_modules(source_dir: Path) -> set[str]:
    """ディレクトリ内の .py が import しているトップレベルモジュール名を集める。"""
    modules: set[str] = set()
    for path in sorted(source_dir.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            # `import x.y` と `from x.y import z` で属性名が違うため分けて拾う
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                modules.add(node.module.split(".")[0])
    return modules


def find_non_stdlib_imports(source_dir: Path) -> set[str]:
    """import のうち標準ライブラリでも PoC 内モジュールでもないものを返す。"""
    local_modules = {path.stem for path in source_dir.glob("*.py")}
    known = sys.stdlib_module_names | local_modules | {"__future__"}
    return collect_imported_modules(source_dir) - known


def find_loaded_site_packages() -> set[str]:
    """PoC の実行が持ち込んだ site-packages 由来モジュールを返す。"""
    loaded: set[str] = set()
    for name, module in list(sys.modules.items()):
        origin = getattr(getattr(module, "__spec__", None), "origin", None)
        if origin is not None and "site-packages" in origin:
            loaded.add(name.split(".")[0])
    # venv が起動時に差し込むモジュールは PoC の依存ではないので差し引く
    return loaded - _baseline_modules()


def _baseline_modules() -> set[str]:
    """素のインタプリタ起動時点で読み込まれているモジュール名を返す。"""
    probe = subprocess.run(
        [sys.executable, "-c", "import json, sys; print(json.dumps(sorted(sys.modules)))"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {name.split(".")[0] for name in json.loads(probe.stdout)}


def main() -> int:
    """CLI エントリポイント。"""
    parser = argparse.ArgumentParser(description="標準ライブラリのみで動くことを検査する")
    parser.add_argument(
        "--src", type=Path, default=Path(__file__).parent, help="検査対象のディレクトリ"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    external = find_non_stdlib_imports(args.src)
    logger.info(
        "%s import 検査: 外部モジュール %d 件 %s",
        "OK  " if not external else "NG  ",
        len(external),
        sorted(external),
    )

    # 実際に生成を通してから読み込み済みモジュールを見る（動的 import の取りこぼし対策）
    generate_pdf.generate(
        font_path=settings.FONT_PATH, output_path=settings.OUTPUT_PATH, subset=True
    )
    site_packages = find_loaded_site_packages()
    logger.info(
        "%s 実行時検査: site-packages 由来 %d 件 %s",
        "OK  " if not site_packages else "NG  ",
        len(site_packages),
        sorted(site_packages),
    )
    return 1 if external or site_packages else 0


if __name__ == "__main__":
    sys.exit(main())
