# MVP-FOUND-001-ST02: アプリ構成と設定境界を作る

- 親カード: [MVP-FOUND-001](./README.md)

## 成果

WebとCLIが同じ明示的な依存構成を使い、テスト設定で安全に起動できるFlask application factoryと設定境界。

## 依存サブタスク

- [MVP-FOUND-001-ST01](./mvp-found-001-st01-project-tooling.md)

## 親カードとの関係

親カードのapplication factory、明示的DI、Web・ワーカー共通コードベースというAccepted条件を担当する。

## 変更してよい範囲

- `src/jobhunter/`内の設定、composition root、Flask application factory
- 空のBlueprintとFlask CLIコマンドの明示登録
- 設定・起動を検証する単体テストとFlask test clientテスト
- 環境変数の名前と起動方法を説明する開発文書

## 変更してはいけないもの

- 実求人サイトへの通信、Codex CLI実行、外部通知送信
- 業務用route、ORMエンティティ、作業キューの状態遷移
- 実secret、環境固有URL、動的import、自動登録

## 必要な変更

1. 必須・任意設定を型付き設定オブジェクトへ読み込み、起動時に検証する。
2. application factoryでFlask、Blueprint、CLI、依存コンテナ相当の明示的な構成関数を組み立てる。
3. production、development、testの値をコード上のsecretなしで差し替えられるようにする。
4. health確認用の最小HTTP応答と、依存を差し替えたCLI起動確認を実装する。
5. 設定欠落、テスト設定、二重application生成を検証する。

## 完了条件

- application factoryを2回呼び出して独立したアプリを生成できる。
- test clientで最小HTTP応答を確認できる。
- Flask CLIがapplication factory経由で起動する。
- 不足した必須設定を秘密値を表示せずに拒否する。
- 依存の登録先を明示的importから追跡できる。

## 停止条件

- Flask拡張がグローバルSessionまたはimport時副作用を必須とする。
- 設定ソースの優先順位を一意に定義できない。
- health応答に外部サービス接続が必要という新要件が生じる。

## 返却形式

- application factoryとcomposition rootの公開入口
- 設定項目一覧とsecretの扱い
- 追加テストと実行結果
- ST03がDB依存を登録する箇所
