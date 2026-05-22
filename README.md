# Job Search RSS

求人サイトの検索結果を定期収集し、求人の新規掲載・更新・削除を RSS として配信する Python アプリケーションです。

MVP では atGP を対象に、地域・職種・地域と職種の組み合わせを購読条件として登録できます。RSS 生成時には外部サイトへアクセスせず、保存済みの求人スナップショットと変更履歴だけを参照します。

## 主な機能

- 購読条件の登録
  - 地域: 都道府県、市区町村
  - 職種: 職種カテゴリ、職種詳細
  - 地域と職種の組み合わせ
- atGP の地域・職種マスター同期
- 登録済み購読条件から収集条件を導出
- 求人一覧・詳細の収集と共通求人モデルへの変換
- 前回スナップショットとの差分検知
  - `new`: 新規掲載
  - `updated`: 内容更新
  - `deleted`: 掲載終了または検索結果からの消失
- RSS XML の生成
- CLI と FastAPI による操作入口
- APScheduler 連携用の定期収集ジョブ登録部品

## アーキテクチャ概要

このリポジトリはクリーンアーキテクチャ寄りに責務を分けています。

```text
src/job_search_rss/
  domain/          求人、購読条件、収集条件、変更履歴などの中心モデル
  usecase/         購読登録、収集、差分検知、RSS 生成などのアプリケーションルール
  ports/           Repository、SiteAdapter、RssRenderer の抽象インターフェース
  adapters/        atGP 固有の URL、HTML パース、マスター変換
  infrastructure/  SQLite/SQLAlchemy、設定、ログ
  rss/             RSS XML レンダリング
  scheduler/       定期収集ジョブ登録
  api.py           FastAPI エンドポイント
  cli.py           CLI エントリポイント
```

依存方向は外側から内側です。`domain` と `usecase` は FastAPI、SQLAlchemy、HTTPX、Playwright、HTML 構造などの外部技術に依存しません。求人サイト固有の仕様は `adapters/` に閉じ込め、永続化は `infrastructure/` に閉じ込めます。

## 必要要件

- Python 3.12 以上
- SQLite
- atGP へのライブアクセスを行う場合のみネットワークアクセス

## セットアップ

PowerShell 例:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

パッケージをインストールすると、CLI コマンド `job-search-rss` が利用できます。

## 設定

設定は環境変数から読み込まれます。

| 環境変数 | 既定値 | 説明 |
| --- | --- | --- |
| `JOB_SEARCH_RSS_DB_PATH` | `data/job_search_rss.sqlite3` | SQLite DB ファイルの保存先 |
| `JOB_SEARCH_RSS_COLLECTION_INTERVAL_MINUTES` | `60` | 定期収集間隔の分数 |
| `JOB_SEARCH_RSS_LOG_LEVEL` | `INFO` | ログレベル |
| `JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS` | `false` | atGP へのライブアクセス許可 |

ライブ収集は安全のため既定で無効です。`sync-master` と `collect` を実サイトに対して実行する場合は明示的に有効化してください。

```powershell
$env:JOB_SEARCH_RSS_ALLOW_EXTERNAL_ACCESS = "true"
```

## データベース

既定の DB は `data/job_search_rss.sqlite3` です。CLI と API は起動時に SQLAlchemy の `create_all` により現在のスキーマを作成します。

Alembic の設定とマイグレーションは `migrations/` にあります。現時点ではローカル MVP 運用向けに自動スキーマ作成が主経路で、明示的なマイグレーション確認や将来運用のために Alembic ファイルを保持しています。

## CLI の使い方

### マスター同期

atGP の地域・職種マスターを取得し、共通モデルへ正規化して SQLite に保存します。

```powershell
job-search-rss sync-master
```

出力例:

```text
region_count=47
occupation_count=10
```

### 購読条件の登録

地域のみ:

```powershell
job-search-rss subscribe --prefecture Tokyo
```

地域と市区町村:

```powershell
job-search-rss subscribe --prefecture Tokyo --city Shibuya
```

職種のみ:

```powershell
job-search-rss subscribe `
  --occupation-category Engineering `
  --occupation-detail "Backend Engineer"
```

地域と職種:

```powershell
job-search-rss subscribe `
  --prefecture Tokyo `
  --occupation-category Engineering `
  --occupation-detail "Backend Engineer"
```

出力例:

```text
subscription_id=subscription:region:tokyo|occupation:engineering:backend-engineer
rss_path=/rss/subscription:region:tokyo|occupation:engineering:backend-engineer
```

同じ意味の条件は正規化され、同一購読条件として扱われます。

### 収集

登録済み購読条件から収集条件を導出し、atGP から求人を取得して変更履歴を保存します。

```powershell
job-search-rss collect
```

出力例:

```text
change_count=3
succeeded_condition_count=1
failed_condition_count=0
```

収集失敗は収集実行履歴として保存されます。失敗時の不完全な結果をもとに削除検知は行いません。

## API の使い方

ASGI サーバーは MVP の依存関係に含めていません。ローカルで FastAPI を起動する場合は `uvicorn` を追加で入れてください。

```powershell
python -m pip install uvicorn
```

起動例:

```powershell
python -c "from job_search_rss.api import create_app_from_settings; from job_search_rss.infrastructure.settings import load_settings; import uvicorn; uvicorn.run(create_app_from_settings(load_settings()), host='127.0.0.1', port=8000)"
```

### 購読条件を登録する

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/subscriptions `
  -ContentType "application/json" `
  -Body '{"region":{"prefecture":"Tokyo"},"occupation":{"category":"Engineering","detail":"Backend Engineer"}}'
```

レスポンス例:

```json
{
  "subscription_id": "subscription:region:tokyo|occupation:engineering:backend-engineer",
  "rss_url": "/rss/subscription:region:tokyo|occupation:engineering:backend-engineer"
}
```

### RSS を取得する

```powershell
Invoke-WebRequest http://127.0.0.1:8000/rss/subscription:region:tokyo
```

変更種別で絞り込む場合:

```powershell
Invoke-WebRequest "http://127.0.0.1:8000/rss/subscription:region:tokyo?change_type=updated"
```

`change_type` には `new`、`updated`、`deleted` を指定できます。

## 定期収集

`src/job_search_rss/scheduler/` には APScheduler 互換のスケジューラへ定期収集ジョブを登録する部品があります。

- ジョブ ID: `job-search-rss-collection`
- 実行内容:
  - 購読条件から収集条件を同期
  - 各収集条件で求人収集
  - 変更履歴を保存
- 間隔: `JOB_SEARCH_RSS_COLLECTION_INTERVAL_MINUTES` または呼び出し側指定値

実際のプロセス管理、APScheduler の起動・停止、常駐方法はアプリケーション組み込み側で決めます。

## 開発用コマンド

```powershell
python -m pytest
python -m ruff check .
python -m pyright
```

テストは保存済み HTML fixture と fake 実装を中心に構成されています。通常の自動テストは atGP のライブサイトへアクセスしません。

## 受け入れ・運用確認

- 主要な受け入れ観点は `tests/acceptance/` にあります。
- atGP の HTML 構造が現在も想定通りか確認する場合は `docs/atgp_manual_smoke.md` を参照してください。
- fixture の扱いは `docs/test_fixture_policy.md` を参照してください。

## 既知の制約

- MVP の対象サイトは atGP のみです。
- Web UI、ユーザーアカウント、ユーザー別 RSS 所有権はありません。
- doda Challenge 対応は将来追加候補です。
- 複数求人サイト間の同一求人判定は行いません。
- 高度なランキング、おすすめ、詳細な本文差分表示は対象外です。
- SQLite はローカル・小規模運用向けです。高い書き込み並行性や複数ワーカー運用が必要になった場合は PostgreSQL などへの移行を検討してください。
- atGP の HTML 構造や検索パラメータが変わると、adapter が失敗する可能性があります。その場合は部分的に壊れた求人を保存せず、adapter エラーとして扱う設計です。

詳細は `docs/known_constraints.md` も参照してください。

## サイト追加の方針

新しい求人サイトを追加する場合は、まず `SiteAdapter` 実装を追加します。サイト固有の URL、クエリパラメータ、HTML セレクタ、マスター値は adapter に閉じ込め、usecase は既存の `Repository` と `SiteAdapter` の抽象に依存したままにします。

主な追加ポイント:

- `src/job_search_rss/adapters/` に新 adapter を追加
- サイト固有マスター値を `Region` と `Occupation` に正規化
- 求人一覧・詳細を共通 `Job` に変換
- adapter fixture とパーサーテストを追加
- 必要になった時点で CLI/API のサイト選択設定を追加

設計メモは `docs/future_site_addition.md` を参照してください。

## 関連ドキュメント

- `docs/local_operation_guide.md`: ローカル運用手順
- `docs/known_constraints.md`: 既知の制約
- `docs/atgp_adapter_spec.md`: atGP adapter の前提
- `docs/atgp_manual_smoke.md`: atGP ライブ確認手順
- `docs/future_site_addition.md`: サイト追加方針
- `docs/test_fixture_policy.md`: fixture 管理方針
