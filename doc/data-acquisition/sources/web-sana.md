# WebSana

- 状態: Draft

## 取得対象

| 項目 | 値 |
| --- | --- |
| `source_key` | `web_sana` |
| 許可host | `www.web-sana.com` |
| 検索結果path | `/site/srch_dtl.php` |
| 詳細path | `/site/comp_frame.php` |
| 検索結果URL例 | `https://www.web-sana.com/site/srch_dtl.php?sground=40&category=13,16&content_jisseki=17&searchDispOrder=date` |
| 詳細URL例 | `https://www.web-sana.com/site/comp_frame.php?tab=saiyo_c&comp_id=CO927IKV&comp_cate_id=CO927IKV01C001&sub_code=16` |

## 規約・制約

- `tab=saiyo_c`と`comp_id`、`comp_cate_id`、`sub_code`を持つURLだけを求人詳細として扱う。
- 会社IDだけでは求人を一意にできない可能性があるため、3値を順序固定で連結した値を`external_job_id`とする。
- より安定した公式求人IDが確認できた場合は、ID移行方針を別途決定する。

## 取得方式・頻度

- `search_fetch_mode`は`STATIC_HTTP`。
- 詳細リンク候補は`a[href^="/site/comp_frame.php"]`で、query条件も検証する。
- ページングは`.pager a`の`pageID` queryを持つリンクから取得する。
- HTML entityを復号し、相対URLを絶対URLへ変換する。
- 未訪問の正規化済み`pageID`要求がなくなった時点で正常終了する。

## データ変換

- 例では求人IDを`CO927IKV:CO927IKV01C001:16`とする。
- query parameter順序は同一性に影響させない。
- 求人固有領域のallowlist selector、必須見出し、HTTP 200の掲載終了markerは実ページ確認後に定義する。

## エラー・再試行

- 必須queryが欠けた詳細リンクは無視せず解析異常として計数し、閾値超過時は巡回失敗とする。
- 同じ正規化URLへの循環、安全上限到達は巡回失敗とする。

## 監視

- 取得ページ数、query不備リンク数、一意求人ID数
- 同じ`comp_id`に属する求人ID数
- 求人固有領域の抽出成功率と掲載終了判定数

## 関連文書

- [求人サイト別仕様](./README.md)
- [求人サイトアダプター](../source-adapters.md)
