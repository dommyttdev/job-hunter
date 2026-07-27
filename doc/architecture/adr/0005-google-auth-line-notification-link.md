# 0005 Google認証と任意のLINE通知連携を採用する

- 状態: Accepted

## 背景

JobHunterの会員登録・ログイン方式をGoogleへ変更する。LINEは通知チャネルとして引き続き使用するが、すべての利用者がLINE通知を必要とするとは限らない。

Google認証とLINE通知連携では、外部ID、認可目的、解除条件、障害時の影響が異なる。LINE Login callbackをJobHunterへのログインとして扱うと、Google会員との関連が曖昧になり、意図しない会員作成や通知先の取り違えにつながる。

## 決定

- JobHunterの会員登録・ログインにはGoogle OpenID Connectを使用する。
- Google ID tokenの`sub`を外部認証IDとし、メールアドレスを利用者の同一性に使わない。
- LINE LoginをJobHunterへの会員登録・ログインには使用しない。
- LINE通知連携はGoogleログイン済み利用者が明示的にONを選んだ場合だけ開始する。
- LINE Loginは通知先となるLINEアカウントの本人確認だけに使用する。
- LINE連携要求を内部利用者、Webセッション、用途、state、nonce、有効期限に結び付け、1回だけ使用する。
- LINE LoginチャネルとMessaging APIチャネルを同じLINE Provider配下に置く。
- LINE公式アカウントの友だち追加済みを確認した場合だけ通知先を`ACTIVE`にする。
- LINE通知をOFFまたは連携解除しても、Google認証、監視設定、求人履歴を維持する。
- [0003 認証プロバイダーと通知チャネルを分離する](./0003-separate-authentication-and-notification.md)を置き換える。認証と通知を別ポート・別エンティティにする原則は継承する。

## 代替案

- GoogleとLINEの両方をJobHunterログインに使用する方式: アカウント統合と回復フローが必要になり、LINEログインを削除する要件に反するため採用しない。
- Googleログイン時にLINE通知も必須連携する方式: LINE通知を希望しない利用者を不必要な外部認可へ誘導するため採用しない。
- LINE user IDを画面入力させる方式: LINEアカウントの所有を確認できず、誤送信や通知先乗っ取りにつながるため採用しない。
- 友だち追加を確認せず通知先を有効化する方式: Messaging APIの送信条件を満たさず、配信不能状態を有効と誤表示するため採用しない。

## 影響

- Google OAuth clientと、LINE Login・Messaging APIの両チャネルを運用する。
- ログイン画面にはGoogleだけを表示し、LINE連携は通知設定画面だけに表示する。
- LINE callbackはGoogleログイン済みセッションと有効な`notification_link_intent`を必須とする。
- LINE障害、友だち未追加、ブロックはJobHunterログインへ影響しない。
- 既存のLINEログイン利用者データが本番に存在する場合は、Google認証IDを安全に関連付ける移行手順が別途必要になる。実データが存在しない場合は移行不要である。
