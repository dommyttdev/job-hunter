# 求人サイト別仕様

求人サイト固有のURL、求人ID、検索結果の巡回方式、求人固有領域、掲載終了判定をサイトごとに定義します。全サイトに共通する取得契約、正規化、エラー処理は[求人サイトアダプター](../source-adapters.md)を正本とし、個別文書では繰り返しません。

## 対応候補

| `source_key` | サイト | 一覧取得方式 | 個別仕様 |
| --- | --- | --- | --- |
| `doda_challenge` | dodaチャレンジ | ブラウザー、load-more | [dodaチャレンジ](./doda-challenge.md) |
| `atgp` | atGP | HTTP、form GET再構成 | [atGP](./atgp.md) |
| `web_sana` | WebSana | HTTP、query pagination | [WebSana](./web-sana.md) |
| `clover_navi` | クローバーナビ | HTTP、path pagination | [クローバーナビ](./clover-navi.md) |
| `bab_navi` | BABナビ | HTTP、query pagination | [BABナビ](./bab-navi.md) |
| `mynavi_partners` | マイナビパートナーズ紹介 | HTTP、path pagination | [マイナビパートナーズ紹介](./mynavi-partners.md) |

各文書は提供されたURLとDOM例に基づくDraftである。対応を有効化する前に、実ページ、利用規約、robots.txt、詳細ページの求人固有領域、HTTP 200の掲載終了表示を確認し、HTML fixtureで固定する。

## 共通との境界

| 共通仕様 | サイト固有仕様 |
| --- | --- |
| アダプターの型付き操作 | 許可するhost、path、query |
| HTTP・ブラウザー取得器の責務 | `STATIC_HTTP`または`BROWSER`の選択 |
| canonical HTMLの生成規則 | 求人固有領域のallowlist selector |
| SHA-256、`extractor_version` | 求人IDの抽出規則 |
| 再試行、SSRF対策、取得上限 | ページング要素と終了条件 |
| 404を`REMOVED`とする規則 | HTTP 200の掲載終了marker |
| fixtureの共通契約 | サイト固有fixtureと期待値 |

[求人情報の取得へ戻る](../README.md)
