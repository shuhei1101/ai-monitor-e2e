---
template_version: 1.0.0
---

# uuid

Python 標準ライブラリの UUID（RFC 4122）生成モジュール。

乱数ベースの UUID version 4 を含む 4 種類の生成関数と、UUID を表す `UUID` オブジェクトを提供する。

## 現在のバージョン情報

| 項目 | 内容 | 補足 |
| --- | --- | --- |
| バージョン | Python 3.12 標準ライブラリ | 2026-08-07 時点。Python 本体のバージョンに従う |
| ライセンス | PSF License | Python 本体に同梱 |
| 公式 URL | https://docs.python.org/3/library/uuid.html | - |
| 公式ドキュメント | https://docs.python.org/3/library/uuid.html | - |

## インストール手順

標準ライブラリのためインストール不要。

```python
import uuid
```

## API 一覧

バージョン: Python 3.12 標準ライブラリ

| 種別 | 名前 | 用途 | 補足 |
| --- | --- | --- | --- |
| 関数 | [`uuid4()`](#uuid4) | 乱数ベースの UUID version 4 を生成する | タスク ID の採番に使う |
| クラス | [`UUID`](#uuid-1) | UUID 1 件を表すオブジェクト | 生成関数の戻り値の型 |

### `uuid4()`

乱数ベースの UUID version 4 を生成する。

#### パラメータ

なし。

パラメータ例:

```python
import uuid

task_id = str(uuid.uuid4())
```

#### 戻り値

| 型 | 説明 | 補足 |
| --- | --- | --- |
| [`UUID`](#uuid-1) | 生成された UUID version 4 | 文字列が欲しい場合は `str()` に通す |

戻り値例:

```python
UUID('6f1e6bcb-2e2e-4a1e-9c1e-6a6f2d9b1c34')
```

### `UUID`

UUID 1 件を表すイミュータブルなオブジェクト。

#### パラメータ

| パラメータ | 型 | 必須 | 既定 | 説明 | 補足 |
| --- | --- | --- | --- | --- | --- |
| `hex` | `str` | 任意 | `None` | 32 桁の 16 進文字列（ハイフン有無どちらも可） | 既存の UUID 文字列を復元するときに使う |
| `bytes` | `bytes` | 任意 | `None` | 16 バイトのビッグエンディアン表現 | - |
| `int` | `int` | 任意 | `None` | 128 bit 整数表現 | - |
| `version` | `int` | 任意 | `None` | UUID のバージョン（1 / 3 / 4 / 5） | 指定するとバージョンビットを上書きする |

パラメータ例:

```python
import uuid

restored = uuid.UUID("6f1e6bcb-2e2e-4a1e-9c1e-6a6f2d9b1c34")
```

#### 主なプロパティ

| フィールド | 型 | 説明 | 補足 |
| --- | --- | --- | --- |
| `hex` | `str` | ハイフンなしの 32 桁 16 進文字列 | - |
| `int` | `int` | 128 bit 整数表現 | - |
| `version` | `int` | UUID のバージョン番号 | `uuid4()` の戻り値は `4` |

プロパティ例:

```python
str(restored)   # '6f1e6bcb-2e2e-4a1e-9c1e-6a6f2d9b1c34'
restored.hex    # '6f1e6bcb2e2e4a1e9c1e6a6f2d9b1c34'
restored.version  # 4
```
