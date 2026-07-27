# アーキテクチャ

システム全体の構造、責務分担、データの流れを説明するドキュメントを配置します。

## 文書

- `system-context.md` — 利用者、外部求人サービス、通知サービスとの関係
- [求人変更監視システム](./system-design.md) — 取得、保存、変更検知、要約、通知の全体設計
- [技術スタック](./technology-stack.md) — Flask、Jinja2、SQLAlchemy、SQLiteの採用方針と制約
- [Webバックエンド](./web-backend.md) — Google認証、監視設定、求人照会、LINE通知連携
- `data-flow.md` — 取得から通知までの処理とデータの流れ
- [求人監視データモデル](./data-model.md) — 求人、求人固有HTML版、変更イベント、通知などのモデル
- `quality-attributes.md` — 可用性、性能、拡張性、保守性に関する方針
- [ADR](./adr/README.md) — 重要な設計判断とその理由

[ドキュメント一覧へ戻る](../README.md)
