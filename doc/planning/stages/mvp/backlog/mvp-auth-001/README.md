# MVP-AUTH-001: 利用者境界を確立する

- 状態: Current
- カード状態: Planned
- バックログ索引: [MVPバックログ](../README.md)

## 目的

Google OpenID Connectで利用者を認証し、セッション、データ所有権、アカウント削除をWebとアプリケーションサービスの境界で一貫して強制する。

## Ready判定

- `MVP-FOUND-001`が`Accepted`である。
- Google OIDCの登録情報、callback URL、テスト用プロバイダー境界を準備できる。
- CSRF、cookie、再認証を含むセキュリティ設定が確定している。

## Accepted判定

- Google callbackとID tokenを検証し、provider内subjectで同じ利用者へ解決できる。
- 推測不能な参照値を持つサーバー側セッションを作成、更新、失効できる。
- すべての利用者データ操作で所有者IDを検索条件に含める。
- 直近認証を確認したアカウント削除が利用者固有データと作業を削除・中止する。

## 確定済み仕様

- 外部IDやメールアドレスを内部利用者IDにしない。
- 認証プロバイダーは型付き境界と明示登録で追加可能にする。
- LINE LoginはJobHunterの登録・ログインに使用しない。
- LINE連携不能でもGoogleログインとWeb閲覧を利用可能に保つ。
- アカウント削除時、他利用者が参照する共有求人は維持する。

## 受入条件

- state、nonce、issuer、audience、署名、時刻条件を検証し、不正callbackを拒否する。
- ログイン時にsession fixationを防ぎ、ログアウトと期限切れでセッションを無効化する。
- 他利用者のIDを指定したHTTP要求とサービス呼び出しの両方を拒否する。
- CSRF対象の状態変更要求をtokenなしでは受け付けない。
- アカウント削除後に旧セッションを再利用できず、共有求人の参照整合性が保たれる。

## 対象外

- LINE通知先連携、管理者認証、複数Google identityの統合
- メール・パスワード認証、権限ロール、組織アカウント

## 停止条件

- callback、cookie、secretを安全に設定できる実行環境がない。
- アカウント削除時の共有データ境界を既存データモデルで表現できない。
- Google OIDCのテスト代替が本番検証を迂回できる構造になる。

## サブタスク構成

依存解消後、認証プロバイダー、セッション、所有権テスト、アカウント削除を独立してコミット可能か精査する。

## 根拠文書

- [Webバックエンド](../../../../../architecture/web-backend.md)
- [求人監視データモデル](../../../../../architecture/data-model.md)
- [ADR 0003](../../../../../architecture/adr/0003-separate-authentication-and-notification.md)
- [ADR 0005](../../../../../architecture/adr/0005-google-auth-line-notification-link.md)

[MVPバックログへ戻る](../README.md)
