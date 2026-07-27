"""shelve の CRUD / 一括書き込み性能 / 型の往復を実測する PoC。"""

from __future__ import annotations

import argparse
import dbm
import shelve
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

BULK_WRITE_COUNT = 1000
BULK_CONTENT_LENGTH = 100


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """タスク 1 件。"""

    id: str
    title: str
    content: str = ""


def report_backend(base_dir: Path) -> str:
    """shelve が実際に使う内部バックエンドの実装名を返す。"""
    path = str(base_dir / "backend_probe")
    with shelve.open(path) as db:
        impl = type(db.dict)
    return f"{dbm.whichdb(path)}（{impl.__module__}.{impl.__qualname__}）"


def verify_crud(base_dir: Path) -> None:
    """作成 → 書き込み → 取得 → 更新 → 削除 を一連で流して結果を出力する。"""
    path = str(base_dir / "crud")

    # 作成 + 書き込み: ファイルが存在しない状態から開く
    with shelve.open(path) as db:
        db["t1"] = Task(id="t1", title="買い物", content="牛乳")

    # 取得: 開き直して永続化されているかを見る
    with shelve.open(path) as db:
        print(f"[CRUD] 取得: {db['t1']}")

    # 更新: 同じキーへの再代入
    with shelve.open(path) as db:
        db["t1"] = Task(id="t1", title="買い物", content="牛乳とパン")

    with shelve.open(path) as db:
        print(f"[CRUD] 更新後: {db['t1']}")

    # 削除
    with shelve.open(path) as db:
        del db["t1"]

    with shelve.open(path) as db:
        print(f"[CRUD] 削除後のキー有無: {'t1' in db} / 全キー: {list(db.keys())}")


def measure_bulk_write(base_dir: Path, *, writeback: bool) -> float:
    """1000 件の書き込みを close によるフラッシュ込みで計測し経過秒数を返す。"""
    path = str(base_dir / f"bulk_writeback_{writeback}")
    start = time.perf_counter()
    with shelve.open(path, writeback=writeback) as db:
        for i in range(BULK_WRITE_COUNT):
            db[f"t{i}"] = Task(id=f"t{i}", title=f"タスク{i}", content="x" * BULK_CONTENT_LENGTH)
    return time.perf_counter() - start


def verify_roundtrip(base_dir: Path) -> None:
    """str / int / None が書き込み時と同じ型で取り出せるかを出力する。"""
    path = str(base_dir / "roundtrip")
    written: dict[str, object] = {"title": "買い物", "priority": 3, "due_date": None}

    with shelve.open(path) as db:
        for key, value in written.items():
            db[key] = value

    with shelve.open(path) as db:
        # 書き込み時と読み出し後の型を 1 件ずつ突き合わせる
        for key, value in written.items():
            read = db[key]
            print(
                f"[型] {key}: 書込 {type(value).__name__} → 読出 {type(read).__name__}"
                f" / 一致={type(read) is type(value)} / 値={read!r}"
            )


def run(base_dir: Path) -> None:
    """3 観点の検証を順に実行する。"""
    print(f"[環境] 内部バックエンド: {report_backend(base_dir)}")
    print(f"[環境] 検証ディレクトリ: {base_dir}")

    verify_crud(base_dir)

    # writeback は既定の逐次 pickle 化とキャッシュ経由で差が出るため両方測る
    for writeback in (False, True):
        elapsed = measure_bulk_write(base_dir, writeback=writeback)
        print(f"[性能] writeback={writeback}: {BULK_WRITE_COUNT} 件 {elapsed:.3f} 秒")

    verify_roundtrip(base_dir)


def main() -> None:
    """検証ディレクトリを用意して検証を実行する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        help="検証用ファイルの作成先。未指定ならシステムの一時ディレクトリを使う",
    )
    args = parser.parse_args()

    # 保存先による性能差を見るため、指定があればそのディレクトリで計測する
    if args.dir is not None:
        base_dir = Path(args.dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        run(base_dir)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            run(Path(tmp))


if __name__ == "__main__":
    main()
