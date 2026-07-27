# atGP

- 状態: Draft

## 取得対象

| 項目 | 値 |
| --- | --- |
| `source_key` | `atgp` |
| 許可host | `www.atgp.jp` |
| 検索結果path | `/search/top/search_result` |
| 詳細path | `/search/top/search_result_detail/{id}` |
| 検索結果URL例 | `https://www.atgp.jp/search/top/search_result?job_categories=b01001610000005000&prefectures=40&sort_type=1` |
| 詳細URL例 | `https://www.atgp.jp/search/top/search_result_detail/a076000000012t7ife` |

## 規約・制約

- 詳細path末尾の値を`external_job_id`とする。
- IDはサイトfixtureで確認した英数字形式だけを許可する。
- 検索queryはキー順に正規化するが、同じキーの複数値と検索条件を失わない。

## 取得方式・頻度

- `search_fetch_mode`は`STATIC_HTTP`。
- 詳細リンク候補は`a[href*="/search/top/search_result_detail/"]`。
- ページングは`form[action$="/search/top/search_result"]`を解析する。
- `javascript:formPagerN.submit()`を実行せず、formの`action`、`method=get`、全ての成功するinputからGET queryを再構成する。
- `page`以外の`prefectures`、`cities`、`sort_type`なども引き継ぐ。
- 正規化した未訪問ページ要求がなくなった時点で正常終了する。

## データ変換

- `/search_result_detail/a076000000012t7ife`から求人ID`a076000000012t7ife`を得る。
- 求人固有領域のallowlist selector、必須見出し、HTTP 200の掲載終了markerは実ページ確認後に定義する。
- form名やページングclassは識別子として保存しない。

## エラー・再試行

- formから検索条件を復元できない場合は巡回失敗とする。
- 同じ正規化URLへの循環、安全上限到達は巡回失敗とする。

## 監視

- 取得ページ数とページごとの求人ID数
- form解析失敗数、循環検知数
- 求人固有領域の抽出成功率と掲載終了判定数

## 関連文書

- [求人サイト別仕様](./README.md)
- [求人サイトアダプター](../source-adapters.md)
