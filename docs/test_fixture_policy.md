# Test Fixture Policy

## WBS 2.9 テスト用fixture方針

### 基本方針

- 自動テストは実サイトの状態に依存させない。
- ユースケース層のテストはfake実装を使い、FastAPI、SQLAlchemy、HTTPX、Playwright、atGP固有実装へ依存させない。
- 外部アダプタのテストは保存HTMLと期待データを使い、ネットワークアクセスを行わない。
- SQLiteを使う統合テストは一時DBを作成し、テストごとに独立させる。

### fixture配置

- `tests/fakes/`: Repository、SiteAdapter、RssRendererなどのfake実装。
- `tests/fixtures/atgp/`: atGPの保存HTML、期待JSON、パース対象の最小サンプル。
- `tests/fixtures/rss/`: RSS XMLの期待値、XML構造検証用サンプル。
- `tests/fixtures/db/`: SQLite統合テストで使う初期データやマイグレーション検証補助。

### インメモリ実装

- fake Repositoryはテスト内で状態を明示的に作れる単純なインメモリ実装にする。
- テストごとに新しいfakeインスタンスを作り、テスト間で状態を共有しない。
- fakeは本番永続化の全機能を模倣せず、ユースケースが必要とするRepository契約だけを満たす。

### SQLite一時DB

- SQLAlchemy Repositoryの契約テストでは一時SQLite DBを使う。
- ファイルDBが必要なテストはpytestの `tmp_path` 配下に作成する。
- トランザクションやマイグレーションの確認が必要な場合は、インメモリDBではなく一時ファイルDBを優先する。

### 保存HTML

- atGPアダプタのパーステストは保存HTMLを入力にする。
- 保存HTMLは、地域マスター、職種マスター、求人一覧、求人詳細を分けて保持する。
- fixtureには実サイトアクセス日時と、抽出したい期待項目を隣接する期待データとして残す。
- HTML全体が大きすぎる場合は、テスト対象の構造を保った最小HTMLへ削る。

### RSS XML検証

- RSS生成テストは文字列完全一致だけに頼らず、XMLとしてパースして主要要素を検証する。
- 文字コード、Content-Type、GUID、pubDate、title、link、descriptionは個別に確認する。
- RSS生成時にSiteAdapterが呼ばれないことをfakeまたはspyで検証する。

### 実サイトスモーク確認

- 実サイトアクセスは自動テストに含めない。
- atGPの実ページ取得確認は、任意の手動スモーク手順として分離する。
- 手動スモーク確認で得たHTMLを自動テストへ使う場合は、保存HTML fixtureとして固定してから利用する。
