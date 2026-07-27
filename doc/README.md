# JobHunter ドキュメント

このディレクトリは、求人情報の自動取得と、求人の新着・更新・削除を検知して通知するシステムに関するドキュメントの入口です。

## はじめに読むもの

1. [プロダクト](./product/README.md) — 目的、対象範囲、用語、要求を確認する
2. [アーキテクチャ](./architecture/README.md) — システム全体の構成と設計判断を理解する
3. 実装対象に応じて、下記の機能別・運用別ドキュメントを参照する

## ドキュメント一覧

| 分類 | 内容 |
| --- | --- |
| [プロダクト](./product/README.md) | 背景、目的、スコープ、ユースケース、機能・非機能要件、用語 |
| [アーキテクチャ](./architecture/README.md) | システム構成、データフロー、ドメインモデル、設計判断（ADR） |
| [求人情報の取得](./data-acquisition/README.md) | 取得元、取得方式、利用規約・robots.txtへの対応、正規化 |
| [変更検知](./change-detection/README.md) | 求人の同一性判定、重複排除、新着・更新・削除の判定ルール |
| [通知](./notification/README.md) | 通知チャネル、通知条件、抑制、再送、メッセージ形式 |
| [運用](./operations/README.md) | 設定、監視、障害対応、セキュリティ、データ保持 |
| [開発](./development/README.md) | 開発環境、テスト方針、リリース手順、コーディング上の約束 |

## ディレクトリ構成

```text
doc/
├── README.md
├── product/
│   └── README.md
├── architecture/
│   ├── README.md
│   └── adr/
│       └── README.md
├── data-acquisition/
│   └── README.md
├── change-detection/
│   └── README.md
├── notification/
│   └── README.md
├── operations/
│   └── README.md
└── development/
    └── README.md
```

詳細な文書は、設計や実装の進行に合わせて各分類へ追加します。未確定事項を事実として記載せず、決定が必要な項目は明示します。

## 文書を追加・更新するとき

- 1つの文書では1つの主題を扱います。
- ファイル名は、内容が分かる英小文字の kebab-case とします。
- 新しい文書へのリンクを、所属ディレクトリの `README.md` に追加します。
- システム全体に影響する重要な設計判断は、[ADR](./architecture/adr/README.md) として残します。
- 実装変更によって仕様や運用方法が変わる場合は、同じ変更内で関連文書も更新します。
