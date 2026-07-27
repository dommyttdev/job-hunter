# dodaチャレンジ

- 状態: Draft

## 取得対象

| 項目 | 値 |
| --- | --- |
| `source_key` | `doda_challenge` |
| 許可host | `doda.jp` |
| 検索結果path | `/challenge/JobSearchList/`配下 |
| 詳細path | `/challenge/JobSearchDetail/` |
| 検索結果URL例 | `https://doda.jp/challenge/JobSearchList/st_S40/jc_JL08/` |
| 詳細URL例 | `https://doda.jp/challenge/JobSearchDetail/?order=1000020682` |

## 規約・制約

- 詳細URLの必須query `order`を`external_job_id`とする。
- `order`は数字だけを許可する。
- 詳細URLはscheme、host、path、`order`を正規化し、追跡用queryとfragmentを除去する。

## 取得方式・頻度

- `search_fetch_mode`は`BROWSER`。
- 詳細リンク候補は`a[href^="/challenge/JobSearchDetail/?"]`。
- `<button type="button">さらに読み込む</button>`をload-more操作として扱う。class名だけを識別根拠にしない。
- 操作ごとにDOMの求人ID集合を再取得し、新規ID数が増えたことを確認する。
- ボタンが存在しないか無効で、求人ID集合が安定した場合に正常終了する。
- ボタンが残ったままIDが増えない場合は、待機と再試行を上限回数まで行い、解消しなければ巡回失敗とする。
- browser network logから正規の同一originページングendpointを確認でき、利用条件上問題がない場合だけHTTP取得への置換を検討する。非公開endpointを推測しない。

## データ変換

- `order=1000020682`から求人ID`1000020682`を得る。
- 求人固有領域のallowlist selector、必須見出し、HTTP 200の掲載終了markerは実ページ確認後に定義する。

## エラー・再試行

- load-moreの途中失敗、安全上限到達、bot対策画面は巡回失敗とし、部分的な新着を確定しない。

## 監視

- load-more操作回数と操作ごとの新規ID増分
- 巡回終了理由と抽出した一意求人ID数
- 求人固有領域の抽出成功率と掲載終了判定数

## 関連文書

- [求人サイト別仕様](./README.md)
- [求人サイトアダプター](../source-adapters.md)
