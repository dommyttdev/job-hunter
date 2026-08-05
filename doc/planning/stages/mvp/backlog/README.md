# MVPバックログ

MVPを実装する親カードのID、概要、永続状態、依存、根拠を管理する正本です。

## 読み方

- 実装順序は[実装優先順位](../implementation-priority.md)を参照する。
- 着手できるのは`Ready`のカードだけとする。
- 依存カードは、原則としてすべて`Accepted`になってから次カードを`Ready`へ変更する。
- 状態の変更時は、この索引と対象カードを同じコミットで更新する。
- 実装中の一時状態はGitHub Issueまたは作業ブランチで扱い、この索引へ追加しない。

## 永続状態

| 状態 | 意味 |
| --- | --- |
| `Unrefined` | 内容と境界が未整理 |
| `Planned` | 目的、範囲、依存を整理済み |
| `Ready` | 単独で着手し、完了判定できる |
| `Blocked` | 判断または依存の解消待ち |
| `Accepted` | 実装、検証、統合が完了 |

## カード一覧

| ID | 概要 | 永続状態 | 依存 | 主な根拠 |
| --- | --- | --- | --- | --- |
| `MVP-FOUND-001` | アプリ、DB、永続作業キュー、テストの実行基盤 | `Ready` | なし | [技術スタック](../../../../architecture/technology-stack.md)、[システム設計](../../../../architecture/system-design.md) |
| `MVP-SOURCE-001` | サイトアダプターによる検索・詳細取得と保存 | `Planned` | `MVP-FOUND-001` | [サイトアダプター](../../../../data-acquisition/source-adapters.md)、[取得元](../../../../data-acquisition/sources/README.md) |
| `MVP-DETECT-001` | 基準化と求人状態イベントの変更検知 | `Planned` | `MVP-FOUND-001`, `MVP-SOURCE-001` | [変更判定ルール](../../../../change-detection/change-rules.md)、[データモデル](../../../../architecture/data-model.md) |
| `MVP-SUMMARY-001` | 現在要約・変更要約と制限時フォールバック | `Planned` | `MVP-DETECT-001` | [システム設計](../../../../architecture/system-design.md)、[要件](../../../../product/requirements.md) |
| `MVP-AUTH-001` | Google認証、セッション、所有権、アカウント削除 | `Planned` | `MVP-FOUND-001` | [Webバックエンド](../../../../architecture/web-backend.md)、[ADR 0003](../../../../architecture/adr/0003-separate-authentication-and-notification.md) |
| `MVP-WEB-001` | 監視設定管理と現在求人のWeb画面 | `Planned` | `MVP-AUTH-001`, `MVP-SOURCE-001`, `MVP-DETECT-001`, `MVP-SUMMARY-001` | [Web UI](../../../../product/web-ui.md)、[Webバックエンド](../../../../architecture/web-backend.md) |
| `MVP-NOTIFY-001` | LINE連携と通常・遅延ダイジェスト | `Planned` | `MVP-AUTH-001`, `MVP-DETECT-001`, `MVP-SUMMARY-001` | [求人変更通知](../../../../notification/job-change-notifications.md)、[ADR 0005](../../../../architecture/adr/0005-google-auth-line-notification-link.md) |
| `MVP-OPS-001` | 観測、安全停止、復旧、MVP縦断検証 | `Planned` | 先行7カード | [運用](../../../../operations/README.md)、[MVP機能範囲](../scope.md) |

## 共通Accepted条件

- カード固有の受入条件を自動テストまたは記録された手動確認で満たす。
- 関連する要件、設計、ADR、運用文書と実装が一致する。
- 追加した設定、外部依存、運用操作が文書化されている。
- 静的検査と関連テストが成功し、既存の成功ケースを壊していない。
- 対象カードとこの索引の状態を同じコミットで`Accepted`へ更新する。

## 運用

1. 依存が解消した`Planned`カードを精査し、受入条件と停止条件が十分なら`Ready`へ変更する。
2. 必要な場合だけ、独立してコミットできるサブタスクへ分割する。
3. 実装者は1枚の`Ready`カードまたは1サブタスクだけを担当する。
4. 完了成果を親カードのAccepted条件と照合し、満たした場合だけ`Accepted`へ変更する。
5. 全カードが`Accepted`になった時点でMVP段階の完了判定を行う。

[MVP計画へ戻る](../README.md)
