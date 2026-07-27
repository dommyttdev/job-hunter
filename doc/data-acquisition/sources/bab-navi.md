# BABナビ

- 状態: Draft

## 取得対象

| 項目 | 値 |
| --- | --- |
| `source_key` | `bab_navi` |
| 許可host | `bab-navi.dandi.co.jp` |
| 検索結果path | `/zenkoku/`配下 |
| 詳細path | `/kyujin/{id}` |
| 検索結果URL例 | `https://bab-navi.dandi.co.jp/zenkoku/MC27,28,29,71` |
| 詳細URL例 | `https://bab-navi.dandi.co.jp/kyujin/7026` |

## 規約・制約

- 詳細pathの`{id}`を`external_job_id`とする。
- IDは数字だけを許可する。

## 取得方式・頻度

- `search_fetch_mode`は`STATIC_HTTP`。
- 詳細リンク候補は`a[href^="/kyujin/"]`。
- ページングは`.mod-pagination a`の`page` queryを持つリンクから取得する。
- `data-page`は0始まり、表示上の`page`は1始まりであるため、要求URLの`page`を正本とする。
- 未訪問の正規化済みページURLがなくなった時点で正常終了する。

## データ変換

- `/kyujin/7026`から求人ID`7026`を得る。
- 求人固有領域のallowlist selector、必須見出し、HTTP 200の掲載終了markerは実ページ確認後に定義する。

## エラー・再試行

- `data-page`とURLの不一致は警告として記録し、URLを優先する。
- 同じ正規化URLへの循環、安全上限到達は巡回失敗とする。

## 監視

- 取得ページ数、一意求人ID数
- `data-page`とURLの不一致数
- 求人固有領域の抽出成功率と掲載終了判定数

## 関連文書

- [求人サイト別仕様](./README.md)
- [求人サイトアダプター](../source-adapters.md)
