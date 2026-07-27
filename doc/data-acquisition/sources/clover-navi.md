# クローバーナビ

- 状態: Draft

## 取得対象

| 項目 | 値 |
| --- | --- |
| `source_key` | `clover_navi` |
| 許可host | `www.clover-navi.com` |
| 検索結果path | `/results/list/`配下 |
| 詳細path | `/detail/index/id/{id}` |
| 検索結果URL例 | `https://www.clover-navi.com/results/list/find/areaid/area_id/13` |
| 詳細URL例 | `https://www.clover-navi.com/detail/index/id/50068` |

## 規約・制約

- 詳細pathの`{id}`を`external_job_id`とする。
- IDは数字だけを許可する。
- `target`、`onclick`、リンク文字列は求人IDとして使用しない。

## 取得方式・頻度

- `search_fetch_mode`は`STATIC_HTTP`。
- 詳細リンク候補は`a[href*="/detail/index/id/"]`。
- ページングは`.membernavi2 a`の`/page/{n}`を含むリンクから取得する。
- 「次のページ」とページ番号が同じURLを指す場合も、正規化URL集合で重複排除する。
- 未訪問の正規化済みページURLがなくなった時点で正常終了する。

## データ変換

- `/detail/index/id/50068`から求人ID`50068`を得る。
- 求人固有領域のallowlist selector、必須見出し、HTTP 200の掲載終了markerは実ページ確認後に定義する。

## エラー・再試行

- ページ番号が増えない循環、安全上限到達は巡回失敗とする。

## 監視

- 取得ページ数、一意ページURL数、一意求人ID数
- 重複ページリンク数、ID形式不正数
- 求人固有領域の抽出成功率と掲載終了判定数

## 関連文書

- [求人サイト別仕様](./README.md)
- [求人サイトアダプター](../source-adapters.md)
