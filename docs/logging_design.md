# Logging Design

## 目的

Job Search RSS のログは、ローカル運用で「何が実行され、どこで失敗し、再実行してよいか」を判断できることを主目的にする。
対象ログレベルは `INFO`, `DEBUG`, `WARNING`, `ERROR` とし、通常運用では `INFO`、調査時のみ `DEBUG` を有効にする。

このコードベースは domain / usecase / adapters / infrastructure が分離されているため、ログも同じ境界を保つ。

- domain: ログを出さない。値オブジェクトとビジネス不変条件を純粋に保つ。
- usecase: 業務イベント、件数、成功/失敗結果を出す。
- adapters: 外部サイト、HTTP、Playwright、HTML パースなど外部境界の詳細を出す。
- infrastructure: DB 接続、設定読み込み、ログ初期化など実行基盤を出す。
- cli/api/scheduler: リクエストまたはコマンド単位の開始/終了/失敗を出す。

既存の `job_search_rss.infrastructure.logging.log_event()` は、イベント名と追加コンテキストを `LogRecord.extra` に載せる構造化ログの入口として使う。

## ロガー構成

アプリケーションロガー名は既存の `job_search_rss` を継続する。

- logger name: `job_search_rss`
- event field: `event`
- default level: `JOB_SEARCH_RSS_LOG_LEVEL`、未指定時 `INFO`
- output: 当面は標準エラー
- format: ローカル可読性を優先しつつ、`event` と主要 context を失わない形式

推奨する初期化 API:

```python
configure_logging(level: str) -> None
```

CLI と API の起動入口で `load_settings().log_level` を渡して呼び出す。テストでは `caplog` で `log_event()` の `extra` を検証できる状態を維持する。

## 共通フィールド

全イベントに可能な限り付与する。

| field | 内容 | 備考 |
| --- | --- | --- |
| `event` | 機械可読なイベント名 | snake_case |
| `component` | `cli`, `api`, `scheduler`, `usecase`, `adapter`, `repository` | 粒度の入口 |
| `operation` | `subscribe`, `collect`, `sync_master`, `generate_rss` など | ユースケース名 |
| `site_id` | `atgp` など | サイト追加時の切り分け用 |
| `subscription_id` | RSS 購読 ID | 個人情報そのものではないが長くなる点に注意 |
| `collection_condition_key` | 収集条件キー | 失敗再実行の単位 |
| `job_id` | 求人 ID | 求人単位の調査用 |
| `attempt` | リトライ回数 | 1 始まり |
| `elapsed_ms` | 処理時間 | 外部 I/O と usecase 完了時に有効 |
| `count` 系 | `job_count`, `change_count`, `region_count` など | 集計は INFO、詳細は DEBUG |
| `error_type` | 例外クラス名 | ERROR/WARNING |
| `reason` | 失敗理由の短い分類 | 例: `fetch_error`, `parse_error`, `validation_error` |

ログに HTML 本文、RSS XML 全文、求人本文の詳細、HTTP レスポンス本文は出さない。URL は atGP の検索/詳細 URL まで許容するが、将来トークンや個人識別子を含む URL を扱う場合はマスクする。

## レベル設計

### INFO

通常運用で追うべきライフサイクルイベントを出す。件数、成功/失敗数、対象キーを含める。

主な用途:

- CLI コマンド開始/終了
- API リクエストの主要業務イベント
- 定期収集ジョブ登録/開始/終了
- 購読条件の登録、既存条件の再利用
- 収集条件の作成
- 収集バッチ全体の開始/終了
- 条件単位の収集成功
- マスター同期成功
- RSS 生成成功

例:

- `command_started`
- `command_completed`
- `subscription_registered`
- `subscription_reused`
- `collection_started`
- `collection_condition_completed`
- `collection_completed`
- `site_master_sync_completed`
- `rss_generated`

### DEBUG

障害調査や実装確認に必要な詳細を出す。通常運用では出ない前提にする。

主な用途:

- 設定値の読み込み結果。ただし secret は出さない。
- atGP 検索 URL の組み立て結果
- ページ fetch 開始/終了、ページ単位の求人件数
- マスターキャッシュ hit/miss
- パース対象件数、重複排除前後の件数
- 差分検出の内訳
- DB repository の高頻度メソッド詳細は原則出さず、必要時のみ境界操作の件数を出す。

例:

- `settings_loaded`
- `atgp_search_url_built`
- `page_fetch_started`
- `page_fetch_completed`
- `atgp_page_parsed`
- `master_cache_missed`
- `job_change_detected`
- `rss_query_filtered`

### WARNING

処理は継続できるが、運用者が知るべき劣化や部分失敗を出す。

主な用途:

- 条件単位の収集失敗を記録し、バッチ全体は継続する場合
- リトライ可能な外部アクセス失敗
- 期待しない HTML 構造だがスキップ可能な行がある場合
- RSS 生成で変化履歴に対応する求人が存在せず、項目を除外した場合
- 外部アクセスが設定で無効なため live collection を開始できない場合

例:

- `collection_condition_failed`
- `collection_retry_scheduled`
- `atgp_partial_parse_skipped`
- `rss_item_skipped_missing_job`
- `external_access_disabled`

### ERROR

リクエスト、コマンド、スケジュールジョブなどの実行単位が失敗して終了する場合に出す。

主な用途:

- CLI コマンドが非 0 終了になる例外
- API 内で想定外例外により 5xx になる例外
- scheduler のジョブ関数が失敗してジョブ実行が落ちる場合
- DB 初期化失敗
- マスター同期全体が失敗し、保存結果が信頼できない場合

例:

- `command_failed`
- `api_request_failed`
- `scheduled_collection_failed`
- `database_initialization_failed`
- `site_master_sync_failed`

`ERROR` では `exc_info=True` を許可する。`WARNING` ではスタックトレースは原則出さず、調査が必要な外部 I/O 例外のみ `DEBUG` に詳細を分ける。

## モジュール別イベント

### CLI: `src/job_search_rss/cli.py`

`main()` でコマンド名を確定した直後にログ初期化し、各 command の前後を記録する。

| 場所 | level | event | context |
| --- | --- | --- | --- |
| parse 後 | INFO | `command_started` | `command` |
| 正常終了 | INFO | `command_completed` | `command`, result counts |
| validation error | ERROR | `command_failed` | `command`, `error_type`, `reason=validation_error` |
| external disabled | WARNING または ERROR | `external_access_disabled` / `command_failed` | `command=collect|sync-master` |

CLI の標準出力は既存通り機械的な結果表示に使い、ログは標準エラーに出す。

### API: `src/job_search_rss/api.py`

FastAPI 自体の access log に依存せず、業務イベントだけをアプリログに出す。

| エンドポイント | level | event | context |
| --- | --- | --- | --- |
| `POST /subscriptions` 成功 | INFO | `subscription_registered` or `subscription_reused` | `subscription_id` |
| `POST /subscriptions` 400 | WARNING | `subscription_rejected` | `reason=validation_error` |
| `GET /rss/{subscription_id}` 成功 | INFO | `rss_generated` | `subscription_id`, `item_count`, `change_type_count` |
| `GET /rss/{subscription_id}` 404 | WARNING | `subscription_not_found` | `subscription_id` |

想定外例外は FastAPI の例外ハンドラで `api_request_failed` として ERROR に集約する設計が望ましい。

### Scheduler: `src/job_search_rss/scheduler/__init__.py`

定期実行は無人運用の入口なので、登録と実行結果を INFO に残す。

| 場所 | level | event | context |
| --- | --- | --- | --- |
| ジョブ登録 | INFO | `scheduled_collection_registered` | `interval_minutes`, `job_id` |
| ジョブ開始 | INFO | `scheduled_collection_started` | `job_id` |
| ジョブ終了 | INFO | `scheduled_collection_completed` | `change_count`, `succeeded_condition_count`, `failed_condition_count` |
| ジョブ失敗 | ERROR | `scheduled_collection_failed` | `error_type` |

### Usecase

#### `RegisterSubscriptionCondition`

- INFO `subscription_registered`: 新規保存した場合
- INFO `subscription_reused`: 既存条件を返した場合
- WARNING `subscription_registration_rejected`: 入力が不足している legacy path の場合

#### `ManageCollectionCondition`

- INFO `collection_condition_created`: 購読条件から新しい収集条件を作った場合
- DEBUG `collection_condition_reused`: 既存条件を再利用した場合
- INFO `collection_conditions_managed`: 実行結果の総数、新規作成数

#### `RunCollection`

- INFO `collection_started`: 条件数、最大試行回数
- INFO `collection_condition_started`: 条件単位の開始
- INFO `collection_condition_completed`: 条件単位の成功、求人数、差分数
- WARNING `collection_condition_failed`: 条件単位の失敗。バッチは継続。
- WARNING `collection_retry_scheduled`: 次の試行がある場合
- INFO `collection_completed`: 差分数、成功条件数、失敗条件数
- DEBUG `collection_condition_delay_started`: 条件間 delay

#### `DetectJobChanges`

- DEBUG `job_change_detected`: `job_id`, `change_type`
- INFO `collection_run_saved`: 成功/失敗の実行履歴を保存した事実
- WARNING `collection_condition_failed`: 現状ここで例外を握って失敗 run を保存しているため、例外変換点としてログを出す

`DetectJobChanges` は現在 `except Exception` で失敗を `CollectionRun.failed` に変換して空配列を返す。ここは「処理継続できる条件単位の失敗」なので `WARNING` が適切。

#### `SyncSiteMaster`

- INFO `site_master_sync_started`
- DEBUG `site_master_deduplicated`: 重複排除前後
- INFO `site_master_sync_completed`: region / occupation / site mapping 件数
- ERROR `site_master_sync_failed`: 同期全体が例外終了する場合

#### `GenerateRssFeed` / `QueryJobChangesForRss`

- INFO `rss_generated`: RSS item 件数
- DEBUG `rss_query_filtered`: 条件、change type、抽出件数
- WARNING `rss_item_skipped_missing_job`: change に対応する job がない場合

### Adapters: `src/job_search_rss/adapters/atgp.py`

atGP はもっとも壊れやすい境界なので、INFO は大きな単位、DEBUG はページ単位にする。

| 場所 | level | event | context |
| --- | --- | --- | --- |
| URL build | DEBUG | `atgp_search_url_built` | `collection_condition_key`, `url` |
| fetch 開始 | DEBUG | `page_fetch_started` | `url`, `timeout_seconds` |
| fetch 成功 | DEBUG | `page_fetch_completed` | `url`, `elapsed_ms`, `content_length` |
| fetch 失敗 | WARNING | `page_fetch_failed` | `url`, `error_type` |
| list page parse | DEBUG | `atgp_job_list_parsed` | `url`, `job_count`, `has_next_page` |
| detail parse 失敗 | WARNING | `atgp_job_detail_parse_failed` | `job_id`, `reason=parse_error` |
| master fetch 開始/終了 | INFO | `atgp_master_fetch_started` / `atgp_master_fetch_completed` | `master_type`, `count` |
| master cache | DEBUG | `master_cache_hit` / `master_cache_missed` | `master_type` |

HTML パース関数自体は純粋関数として保ち、呼び出し元で件数や例外をログ化する。

### Infrastructure

#### Settings

- DEBUG `settings_loaded`: `db_path`, `collection_interval_minutes`, `log_level`, `allow_external_access`

#### Database

DB 操作ごとの DEBUG ログはノイズが大きいため、初期化と重大エラーに限定する。

- INFO `database_schema_created`: `db_path` または `db_url` の種別
- ERROR `database_initialization_failed`: 起動不能な DB エラー

Repository メソッドの個別ログは、性能問題を調査する段階で SQLAlchemy echo や計測ログとして別途導入する。

## 実装順序

1. `configure_logging(level: str)` を `infrastructure.logging` に追加し、`JOB_SEARCH_RSS_LOG_LEVEL` を CLI/API で適用する。
2. `log_event()` に `exc_info` を渡せるようにし、`ERROR` のスタックトレースを扱えるようにする。
3. CLI と scheduler の開始/終了/失敗ログを追加する。運用価値がもっとも高く、影響範囲が小さい。
4. `RunCollection` と `DetectJobChanges` に条件単位の INFO/WARNING を追加する。
5. atGP adapter に DEBUG/WARNING を追加する。HTML 本文を出さないテストを含める。
6. API に業務イベントと想定外例外ハンドラの ERROR を追加する。
7. RSS 生成の件数ログと missing job の WARNING を追加する。

## テスト方針

既存の `tests/test_logging.py` を拡張し、以下を確認する。

- `log_event()` が `event` と context を `LogRecord.extra` に載せる。
- `configure_logging()` が `INFO`, `DEBUG`, `WARNING`, `ERROR` を受け付ける。
- 不正なログレベルは `ValueError` または `INFO` fallback のどちらかに統一する。運用ミスを早く検出するため `ValueError` を推奨する。
- `ERROR` で `exc_info` が記録できる。

ユースケーステストでは、件数やイベント名など運用契約になるログだけを検証する。DEBUG の細かいイベントは実装変更で壊れやすいため、テストは最小限にする。

## 採用しないこと

- domain 層への logger 注入
- HTML/XML/求人本文の全文ログ
- Repository 全メソッドの逐次 INFO ログ
- 外部の構造化ログライブラリ導入
- DB にアプリログを保存すること

MVP では Python 標準の `logging` と既存の `log_event()` を伸ばす。JSON ログ、OpenTelemetry、メトリクス連携は、常駐運用や複数環境運用が必要になった段階で追加する。
