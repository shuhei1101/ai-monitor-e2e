"""epic #82 PoC: pathlib.Path での一時ファイル生成・書き込み・読み戻し。"""

import sys
import tempfile
import time
from pathlib import Path

PAYLOAD = "hello poc"
USED_MODULES = {"pathlib", "tempfile", "sys", "time"}


def main() -> int:
    tmpdir = Path(tempfile.gettempdir())
    target = tmpdir / "poc_tempfile.txt"

    t0 = time.perf_counter()
    target.write_text(PAYLOAD)
    write_ms = (time.perf_counter() - t0) * 1000

    exists = target.exists()

    t1 = time.perf_counter()
    restored = target.read_text()
    read_ms = (time.perf_counter() - t1) * 1000

    match = restored == PAYLOAD
    non_stdlib = USED_MODULES - sys.stdlib_module_names

    target.unlink(missing_ok=True)

    print(f"target        : {target}")
    print(f"exists        : {exists}")
    print(f"write_text ms : {write_ms:.3f}")
    print(f"read_text ms  : {read_ms:.3f}")
    print(f"restored      : {restored!r}")
    print(f"match payload : {match}")
    print(f"non-stdlib use: {non_stdlib or 'none'}")

    ok = exists and match and not non_stdlib
    print(f"verdict       : {'OK' if ok else 'NG'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
