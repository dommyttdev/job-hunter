# Architecture Decision Records

システム全体に影響する重要な設計判断を、背景や代替案とともに記録します。

## ファイル命名

```text
NNNN-short-title.md
```

例: `0001-job-identity-strategy.md`

## ADR に含める項目

- 状態（提案、採用、廃止、置換）
- 背景
- 決定
- 代替案
- 影響

採用済みの判断を変更するときは元の記録を消さず、新しい ADR から置き換える ADR を参照します。

## 記録

- [0001 求人サイト差異を明示的なアダプターで分離する](./0001-explicit-source-adapters.md)
- [0002 Flask、Jinja2、SQLAlchemy、SQLiteを採用する](./0002-flask-jinja-sqlalchemy-sqlite.md)
- [0003 認証プロバイダーと通知チャネルを分離する](./0003-separate-authentication-and-notification.md)

[アーキテクチャへ戻る](../README.md)
