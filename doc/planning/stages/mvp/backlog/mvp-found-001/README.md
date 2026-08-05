# MVP-FOUND-001: 実行基盤を構築する

- 状態: Current
- カード状態: Ready
- バックログ索引: [MVPバックログ](../README.md)

## 目的

後続カードが同じ構成、DB接続、作業実行方式、テスト方式を使って独立に追加できる、最小のPythonアプリケーション基盤を作る。

## Ready判定

- 採用する中核技術と単一ホスト構成がADR 0002で確定している。
- Webとワーカーを同一コードベースに置き、外部処理をHTTPリクエスト外で行う境界が設計済みである。
- 未決のバージョン、マイグレーション手段、実行コマンドは本カード内で比較・固定できる。

## Accepted判定

- 新規環境で依存関係を導入し、Web、CLI、テストを文書どおり実行できる。
- application factoryが設定と明示的な依存関係を組み立てる。
- SQLite接続でforeign keys、WAL、`busy_timeout`が有効である。
- スキーマを空DBへ適用でき、永続作業を投入、lease、成功、再試行できる。
- CI相当の静的検査とテストが成功する。

## 確定済み仕様

- Python、Flask、Jinja2、SQLAlchemy、SQLiteの単一コードベースとする。
- route、アプリケーションサービス、repository、外部アダプターを分離し、依存を明示登録する。
- SessionはWebリクエストまたはワーカーの1処理単位で生成し、外部処理中はDBトランザクションを保持しない。
- Flask CLIから期限切れ作業を1回分処理できる入口を持つ。
- 設定値とsecretはコードへ埋め込まず、テスト用設定と本番用設定を分離する。

## 受入条件

- 空の作業環境からセットアップ手順だけでテストが成功する。
- 一時SQLite DBを使う統合テストで、設定した接続特性と作業キューの状態遷移を確認できる。
- 同じ重複排除キーの作業を再投入しても作業が重複しない。
- lease期限切れ作業を再取得でき、試行上限到達後は失敗状態になる。
- リフレクション、自動探索、Service Locatorを使わず依存先をコード検索で追跡できる。

## 対象外

- 求人サイト取得、求人エンティティ、変更検知、認証、画面、要約、LINE通知の業務実装
- 複数ホスト対応、外部キュー、サーバー型DB、本番インフラの構築
- 将来カードのための汎用プラグイン機構

## 停止条件

- 対応するPython・ライブラリ版を同時に満たす組み合わせを固定できない。
- マイグレーション手段がSQLiteの制約または配布方式と両立しない。
- 作業キューのleaseと冪等性を既存データモデルで表現できず、設計変更が必要になる。

## サブタスク構成

| 順序 | サブタスク | 依存 | 独立した成果 |
| --- | --- | --- | --- |
| 1 | [ST01 Pythonプロジェクト骨格](./mvp-found-001-st01-project-tooling.md) | なし | 依存管理、パッケージ、品質コマンド |
| 2 | [ST02 アプリ構成と設定境界](./mvp-found-001-st02-app-composition.md) | ST01 | application factory、設定、明示的DI |
| 3 | [ST03 SQLite永続化と作業キュー](./mvp-found-001-st03-persistence-work-queue.md) | ST01、ST02 | マイグレーション、DB接続、永続作業 |
| 4 | [ST04 基盤の縦断検証](./mvp-found-001-st04-foundation-verification.md) | ST01、ST02、ST03 | 再現確認、証拠、親カード状態更新 |

各サブタスクは順番に独立コミットする。ST04で全条件を満たすまで親カードを`Accepted`へ変更しない。

## 根拠文書

- [技術スタック](../../../../../architecture/technology-stack.md)
- [システム設計](../../../../../architecture/system-design.md)
- [求人監視データモデル](../../../../../architecture/data-model.md)
- [ADR 0002](../../../../../architecture/adr/0002-flask-jinja-sqlalchemy-sqlite.md)
- [コーディング規約](../../../../../development/coding-guidelines.md)

[MVPバックログへ戻る](../README.md)
