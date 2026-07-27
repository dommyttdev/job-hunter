# エージェント向け Git 運用ルール

## 作業

- `main` へ直接コミットしない。1タスクにつき1ブランチ。
- 開始前に `git status --short --branch` で既存差分を確認する。
- ユーザーの変更・タスク外差分を変更、退避、破棄、コミットしない。競合時は確認する。

## ブランチ

- 形式：`<fix|feat|chore|docsなど>/<英小文字kebab-caseの概要>`
- `codex/`、エージェント名、担当者名を付けない。
- 原則 `main` から作成する。

## コミット

- 関係するパスだけを `git add -- <path>` でステージする。
- 差分、関連テスト、`git diff --cached --check` を確認する。
- 形式：`<type>: <日本語の要約>`。原則ブランチと同じ type を使う。
- 1コミット1変更。生成物・機密情報・タスク外差分を含めない。

## 統合

- ローカルマージ依頼時：検証後、`main` へ `git merge --ff-only <branch>`。
- `--ff-only` 失敗時は強制せず、原因を調査する。不明点・競合は確認する。
- PR依頼時はローカルマージせず、ブランチをpushしてPRを作成する。
- fetch、pull、push、PR、ブランチ削除は依頼範囲内でのみ行う。

## 禁止

- 無断の `git stash`、`git reset --hard`、`git clean -fd`、`git checkout --`
- force push、公開済み履歴の書き換え、検証・Gitフックの無効化

## 完了報告

ブランチ、コミット、検証、merge・push・PR、未コミット差分を報告する。
