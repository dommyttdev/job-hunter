# マイナビパートナーズ紹介

- 状態: Draft

## 取得対象

| 項目 | 値 |
| --- | --- |
| `source_key` | `mynavi_partners` |
| 許可host | `mpt-shoukai.mynavi.jp` |
| 検索結果path | `/recruit/` |
| 詳細path | `/recruit/{id}` |
| 検索結果URL例 | `https://mpt-shoukai.mynavi.jp/recruit/?post_type=recruit&s=&prefecture%5B%5D=tokyo&salary_min=&_keyword=#search-cond-area` |
| 詳細URL例 | `https://mpt-shoukai.mynavi.jp/recruit/14923` |

## 規約・制約

- `/recruit/{id}`だけを詳細URLとし、`/recruit/page/{n}`を求人として扱わない。
- 詳細pathの`{id}`を`external_job_id`とし、数字だけを許可する。
- fragmentの`#search-cond-area`はHTTP要求と検索URLの同一性から除外する。

## 取得方式・頻度

- `search_fetch_mode`は`STATIC_HTTP`。
- 詳細リンク候補は、pathが厳密に`/recruit/{id}`となる`a[href]`。
- ページングは`.nav-links a.page-numbers`の`/recruit/page/{n}`リンクから取得する。
- ページURLに元の検索queryを引き継ぐ。
- dots要素はリンクではないため継続要求にしない。
- 未訪問の正規化済みページURLがなくなった時点で正常終了する。

## データ変換

- `/recruit/14923`から求人ID`14923`を得る。
- 空値queryの表現差を正規化するが、検索条件のキーを無断で削除しない。
- 求人固有領域のallowlist selector、必須見出し、HTTP 200の掲載終了markerは実ページ確認後に定義する。

## エラー・再試行

- ページURLから検索queryが欠落した場合は巡回失敗とする。
- 同じ正規化URLへの循環、安全上限到達は巡回失敗とする。

## 監視

- 取得ページ数、一意求人ID数
- 詳細URLとページURLの誤分類数
- 求人固有領域の抽出成功率と掲載終了判定数

## 関連文書

- [求人サイト別仕様](./README.md)
- [求人サイトアダプター](../source-adapters.md)
