---
template_version: 1.0.0
---

# uuid

## 概要

Python 標準ライブラリの UUID（RFC 4122）生成モジュール。
バージョン 1 / 3 / 4 / 5 の UUID 生成と、`UUID` オブジェクトによる各種表現（文字列・16 進・整数・バイト列）への変換を提供する。

## 現在のバージョン情報

| 項目 | 内容 | 補足 |
| --- | --- | --- |
| バージョン | Python 3.12 標準ライブラリ | 2026-07-28 時点最新。単独のバージョン番号は持たず Python 本体に追従する |
| ライセンス | PSF License | 商用利用可 |
| 公式 URL | https://docs.python.org/3/library/uuid.html | - |
| 公式ドキュメント | https://docs.python.org/3/library/uuid.html | - |

## インストール手順

標準ライブラリのためインストールは不要。
import するだけで使える。

```python
import uuid
```

## API 一覧

バージョン: `Python 3.12 標準ライブラリ`

| 種別 | 名前 | 用途 | 補足 |
| --- | --- | --- | --- |
| 関数 | [`uuid4()`](#uuid4) | 乱数ベースの UUID を生成 | タスク ID の採番に使う |
| クラス | [`UUID`](#uuid-1) | UUID 値を保持し各種表現に変換する | `uuid4()` の戻り値 |

### `uuid4()`

暗号学的乱数から UUID バージョン 4 を生成する。

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
| [`UUID`](#uuid-1) | 生成された UUID バージョン 4 | 122 ビットが乱数。文字列化は `str()` |

戻り値例:

```python
UUID('9f1c4e2a-6b3d-4f8a-9c2e-1d5b7a0e3f46')
```

### `UUID`

UUID 値を保持する不変オブジェクト。
生成済みインスタンスの属性から各種表現を取り出す。

#### パラメータ

| パラメータ | 型 | 必須 | 既定 | 説明 | 補足 |
| --- | --- | --- | --- | --- | --- |
| `hex` | `str` | 任意 | `None` | 32 桁の 16 進文字列から復元 | ハイフン・波括弧・`urn:uuid:` 接頭辞は無視される |
| `bytes` | `bytes` | 任意 | `None` | 16 バイトのビッグエンディアン列から復元 | - |
| `bytes_le` | `bytes` | 任意 | `None` | 16 バイトのリトルエンディアン列から復元 | Windows の GUID 形式 |
| `fields` | `tuple[int, ...]` | 任意 | `None` | 6 要素のフィールドタプルから復元 | - |
| `int` | `int` | 任意 | `None` | 128 ビット整数から復元 | - |
| `version` | `int` | 任意 | `None` | UUID バージョンを上書き | `1` / `3` / `4` / `5` |

`hex` / `bytes` / `bytes_le` / `fields` / `int` はいずれか 1 つだけを指定する。

パラメータ例:

```python
import uuid

restored = uuid.UUID("9f1c4e2a-6b3d-4f8a-9c2e-1d5b7a0e3f46")
```

#### 戻り値

| フィールド | 型 | 説明 | 補足 |
| --- | --- | --- | --- |
| `hex` | `str` | ハイフンなしの 32 桁 16 進文字列 | - |
| `int` | `int` | 128 ビット整数表現 | - |
| `bytes` | `bytes` | 16 バイトのビッグエンディアン列 | - |
| `version` | `int` | UUID バージョン番号 | `uuid4()` 由来なら `4` |
| `urn` | `str` | RFC 4122 の URN 形式 | `urn:uuid:` 接頭辞付き |

戻り値例:

```python
str(restored)      # '9f1c4e2a-6b3d-4f8a-9c2e-1d5b7a0e3f46'
restored.hex       # '9f1c4e2a6b3d4f8a9c2e1d5b7a0e3f46'
restored.version   # 4
```
