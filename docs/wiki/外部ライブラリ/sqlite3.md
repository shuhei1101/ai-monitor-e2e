---
template_version: 1.0.0
---

# sqlite3

ファイル / インメモリで動く組み込み RDB のクライアント。
SQL でテーブルを定義し、DB-API 2.0 のカーソル経由で読み書きする Python 標準ライブラリ。

## 現在のバージョン情報

| 項目 | 内容 | 補足 |
| --- | --- | --- |
| バージョン | Python 3.12 同梱 | 2026-07-28 時点。同梱される SQLite エンジンのバージョンは `sqlite3.sqlite_version` で確認する（検証時は 3.45.1） |
| ライセンス | PSF License | SQLite エンジン本体は Public Domain。商用利用可 |
| 公式 URL | https://docs.python.org/3/library/sqlite3.html | - |
| 公式ドキュメント | https://docs.python.org/3/library/sqlite3.html | - |

## インストール手順

標準ライブラリのため追加インストールは不要。

```python
import sqlite3
```

- スキーマは SQL で明示的に作る（`CREATE TABLE IF NOT EXISTS ...`）
- 値のバインドは `?` プレースホルダを使い、文字列連結で SQL を組み立てない
- 書き込みは暗黙のトランザクションに入るため、確定には `commit()` が要る
- 書き込みをループ内で 1 件ずつ `commit()` すると fsync が件数分発生して極端に遅くなる。
  1000 件の投入で計測すると、`executemany()` + 単一トランザクションの 0.010 秒に対して件ごと `commit()` は 7.269 秒だった（Python 3.12.3 / WSL2 の ext4 上のファイル DB）。
  絶対値はストレージ依存だが、比率は書き方で決まるため一括書き込みは必ずトランザクションにまとめる
- `str` / `int` / `None` はそれぞれ `str` / `int` / `NoneType` のまま往復する
- Python の `bool` は `INTEGER` 列に `0` / `1` として格納され、取り出すと `int` で戻る。
  真偽値として扱うには取り出し側で `bool()` 変換が要る

## API 一覧

バージョン: Python 3.12 同梱

| 種別 | 名前 | 用途 | 補足 |
| --- | --- | --- | --- |
| 関数 | [`connect()`](#connect) | DB への接続を開く | - |
| コンテキストマネージャ | [`with conn:`](#with-conn) | トランザクション境界（commit / rollback）の管理 | 接続は閉じない |
| メソッド | [`Connection.execute()`](#connectionexecute) | SQL を 1 文実行する | - |
| メソッド | [`Connection.executemany()`](#connectionexecutemany) | 同じ SQL を複数のバインド値で繰り返し実行する | 一括書き込みで使う |
| メソッド | [`Connection.commit()`](#connectioncommit) | トランザクションを確定する | `with conn:` を使う場合は不要 |
| メソッド | [`Connection.close()`](#connectionclose) | 接続を閉じる | 未 commit の変更は失われる |
| 属性 | [`Connection.row_factory`](#connectionrow_factory) | 行の生成方法を差し替える | `sqlite3.Row` とセットで使う |
| メソッド | [`Cursor.fetchone()`](#cursorfetchone) | 結果を 1 行取得する | 該当なしは `None` |
| メソッド | [`Cursor.fetchall()`](#cursorfetchall) | 残りの結果を全件取得する | - |
| 属性 | [`Cursor.rowcount`](#cursorrowcount) | 直前の更新 / 削除が影響した行数 | 更新 / 削除の成否判定に使える |
| クラス | [`sqlite3.Row`](#sqlite3row) | 列名でアクセスできる行 | `row_factory` に設定する |

### `connect()`

DB への接続を開く。
存在しないパスを渡すと DB ファイルが新規作成される。

#### パラメータ

| パラメータ | 型 | 必須 | 既定 | 説明 | 補足 |
| --- | --- | --- | --- | --- | --- |
| `database` | `str or bytes or os.PathLike` | 必須 | - | DB ファイルのパス | `":memory:"` を渡すとインメモリ DB になる（テストで使い分けられる） |
| `timeout` | `float` | 任意 | `5.0` | 他の接続がロックを保持している間に待つ秒数 | 超過すると `OperationalError` |
| `detect_types` | `int` | 任意 | `0`（変換なし） | 宣言型 / 列名から Python 型への変換を有効化 | `PARSE_DECLTYPES` / `PARSE_COLNAMES` のビット OR で指定 |
| `isolation_level` | `str or None` | 任意 | `""` | 暗黙のトランザクション制御 | `""`=書き込み前に自動で BEGIN / `None`=autocommit / `"DEFERRED"`・`"IMMEDIATE"`・`"EXCLUSIVE"`=BEGIN の種類を指定 |
| `check_same_thread` | `bool` | 任意 | `True` | 作成したスレッド以外からの利用を禁止する | `False` にする場合は呼び出し側で排他する |
| `factory` | `type[Connection]` | 任意 | `sqlite3.Connection` | 生成する接続クラス | 独自サブクラスを使う場合のみ指定する |
| `cached_statements` | `int` | 任意 | `128` | プリペアドステートメントのキャッシュ数 | - |
| `uri` | `bool` | 任意 | `False` | `database` を URI として解釈する | `file:tasks.db?mode=ro` のような読み取り専用指定ができる |
| `autocommit` | `bool` | 任意 | `sqlite3.LEGACY_TRANSACTION_CONTROL` | PEP 249 準拠のトランザクション制御に切り替える | Python 3.12 で追加。既定は従来どおり `isolation_level` に従う |

パラメータ例:

```python
import sqlite3

conn = sqlite3.connect("tasks.db")
memory_conn = sqlite3.connect(":memory:")
```

#### 戻り値

| 型 | 説明 | 補足 |
| --- | --- | --- |
| `Connection` | DB への接続 | 使い終えたら `close()` する |

### `with conn:`

トランザクション境界を管理するコンテキストマネージャ。
ブロックを正常に抜けると commit し、例外が送出されると rollback する。
接続そのものは閉じないため、close は別途必要（`contextlib.closing` の併用が使いやすい）。

パラメータはない。

コード例:

```python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect("tasks.db")) as conn:
    with conn:  # ここが commit / rollback の境界
        conn.execute("UPDATE tasks SET priority = ? WHERE id = ?", (5, "t1"))
```

### `Connection.execute()`

SQL を 1 文だけ実行し、結果を読むための `Cursor` を返す。
内部でカーソルを生成するショートカット。

#### パラメータ

| パラメータ | 型 | 必須 | 既定 | 説明 | 補足 |
| --- | --- | --- | --- | --- | --- |
| `sql` | `str` | 必須 | - | 実行する SQL 文 | 値は埋め込まずプレースホルダで渡す |
| `parameters` | `Sequence or dict` | 任意 | `()` | プレースホルダにバインドする値 | 位置指定は `?` とシーケンス、名前指定は `:name` と dict |

パラメータ例:

```python
conn.execute(
    "INSERT INTO tasks (id, title, priority, note) VALUES (?, ?, ?, ?)",
    ("t1", "買い物", 3, None),
)
```

#### 戻り値

| 型 | 説明 | 補足 |
| --- | --- | --- |
| `Cursor` | 実行結果を読むカーソル | `fetchone()` / `fetchall()` / `rowcount` で結果を取る |

### `Connection.executemany()`

同じ SQL を、渡されたバインド値の並びの分だけ繰り返し実行する。
1 トランザクションにまとめた一括書き込みで使う。

#### パラメータ

| パラメータ | 型 | 必須 | 既定 | 説明 | 補足 |
| --- | --- | --- | --- | --- | --- |
| `sql` | `str` | 必須 | - | 実行する SQL 文 | `INSERT` / `UPDATE` / `DELETE` 向け。値を返す文には使えない |
| `parameters` | `Iterable[Sequence or dict]` | 必須 | - | 1 回分ずつのバインド値の並び | ジェネレータも渡せる |

パラメータ例:

```python
rows = [(f"t{i}", f"タスク{i}", i % 5, None) for i in range(1000)]

with conn:
    conn.executemany(
        "INSERT INTO tasks (id, title, priority, note) VALUES (?, ?, ?, ?)", rows
    )
```

#### 戻り値

| 型 | 説明 | 補足 |
| --- | --- | --- |
| `Cursor` | 実行結果を読むカーソル | `rowcount` に全体の影響行数が入る |

### `Connection.commit()`

開いているトランザクションを確定する。
`with conn:` を使う場合はブロック終了時に呼ばれるため、明示的な呼び出しは不要。

パラメータはない。
戻り値は `None`。

### `Connection.close()`

接続を閉じる。
未 commit の変更は破棄されるため、確定してから閉じる。

パラメータはない。
戻り値は `None`。

### `Connection.row_factory`

行の生成方法を差し替える属性。
既定は `None` で、行は列順の `tuple` として返る。

| 設定値 | 行の型 | 補足 |
| --- | --- | --- |
| `None`（既定） | `tuple` | 列順のインデックスでアクセスする |
| `sqlite3.Row` | `sqlite3.Row` | 列名でもインデックスでもアクセスできる |
| 任意の callable | 戻り値次第 | `(cursor, row) -> Any` のシグネチャで受ける |

設定例:

```python
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT id, title FROM tasks WHERE id = ?", ("t1",)).fetchone()
print(row["title"])  # 買い物
```

### `Cursor.fetchone()`

結果セットから 1 行取り出す。

パラメータはない。

#### 戻り値

| 型 | 説明 | 補足 |
| --- | --- | --- |
| `Any or None` | 次の 1 行。残っていなければ `None` | 行の型は `row_factory` に従う（既定は `tuple`） |

戻り値例:

```python
('t1', '買い物', 3, None)
```

### `Cursor.fetchall()`

結果セットの残り全行をリストで取り出す。

パラメータはない。

#### 戻り値

| 型 | 説明 | 補足 |
| --- | --- | --- |
| `list` | 残りの全行 | 該当行がなければ空リスト。行の型は `row_factory` に従う |

戻り値例:

```python
[('t1', '買い物', 3, None), ('t2', '掃除', 1, 'メモ')]
```

### `Cursor.rowcount`

直前に実行した `INSERT` / `UPDATE` / `DELETE` が影響した行数を持つ属性。

| 値 | 意味 | 補足 |
| --- | --- | --- |
| `0` 以上 | 影響した行数 | `UPDATE` / `DELETE` の成否判定に使える（対象が無ければ `0`） |
| `-1` | 行数が確定していない | `SELECT` の実行後や未実行のカーソル |

### `sqlite3.Row`

列名でアクセスできる行を提供するクラス。
`row_factory` に設定して使い、単体でインスタンス化することはない。

| 操作 | 例 | 補足 |
| --- | --- | --- |
| 列名アクセス | `row["title"]` | 大文字小文字は区別しない |
| インデックスアクセス | `row[1]` | `tuple` と同じ位置指定 |
| 列名の一覧 | `row.keys()` | 列名の `list` を返す |
