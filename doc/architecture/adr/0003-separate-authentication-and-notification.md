# 0003 認証プロバイダーと通知チャネルを分離する

- 状態: Accepted

## 背景

初期ログイン方式と通知チャネルはLINEであるため、同じLINE user IDを利用できる構成が可能である。しかし、ログインの成功とMessaging APIによる通知可否は同じ状態ではない。通知には公式アカウントの友だち追加などが必要であり、利用者がブロックした場合もログインは継続できる。

将来はLINE以外のログイン方式や通知チャネルを追加する可能性があり、ログイン方式と通知方式が常に1対1になる保証はない。

## 決定

- 認証は`AuthenticationProvider`、通知は`NotificationChannel`という独立した型付きポートにする。
- 利用者と外部認証IDの関係を`auth_identity`、利用者と通知先の関係を`notification_destination`として別々に保存する。
- ログイン方式に対応する既定通知先の作成方針は、静的な`DefaultNotificationProvisioner`へ明示登録する。
- 初期構成では`line_login`から`line_messaging`の通知先候補を作る。
- LINE LoginチャネルとMessaging APIチャネルを同じLINE Provider配下に配置し、同じuser IDを利用する。
- 通知先にはログイン状態とは独立した`ACTION_REQUIRED`、`ACTIVE`、`BLOCKED`、`DISABLED`状態を持たせる。

## 代替案

- `user`にLINE user IDと通知可否を直接持たせる方式: 初期実装は簡単だが、複数認証方式、複数通知先、ブロック状態を表現しにくいため採用しない。
- 認証プロバイダーが通知も送信する方式: インターフェースの責務が混在し、認証だけまたは通知だけのプロバイダーを追加できないため採用しない。
- ログイン成功時は常に通知可能とみなす方式: LINE Messaging APIの送信条件と一致せず、配信不能を利用者へ説明できないため採用しない。

## 影響

- 初回LINEログイン後も、通知先が`ACTION_REQUIRED`になる場合がある。
- LINEのチャネル作成時に同じProviderへ配置する運用制約が生じる。
- LINE webhookの署名検証とfollow、unfollowイベント処理が必要になる。
- 将来のログイン方式追加では既存通知実装を変更せず、認証アダプターと必要な既定通知先方針だけを追加できる。
- 利用者が複数認証IDまたは複数通知先を持つ将来拡張を妨げない。
