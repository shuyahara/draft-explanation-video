---
description: 台本の修正/新規制作のGitHub Issueを起点として作成する
allowed-tools: Bash(gh issue:*), Bash(gh api:*), Read, Glob, Grep
---

GitHub Issue を起点として立てます。リポジトリは `shuyahara/draft-explanation-video`。

依頼内容: $ARGUMENTS

## 手順

1. 内容から **修正（既存台本の改善）** か **新規（新しい台本）** かを判断する。
   - 判断が曖昧なら、ユーザーに一言確認する。
2. 対象台本が既存なら `scripts/` を確認し、ファイル名・該当シーンを特定して本文に含める。
3. テンプレートに沿って本文を組み立て、`gh issue create` で作成する。
   - 修正: `--label revision`、タイトルは `[修正] {要約}`
   - 新規: `--label new-script`、タイトルは `[新規] {テーマ}`
   - 本文には「問題／期待結果／出典の要否」（修正）または「テーマ／想定尺／結論方向／引用候補」（新規）を含める。
4. 作成した **Issue の URL と番号** を報告し、次アクション（例: `/draft #N` で着手）を提案する。

## 注意

- ラベルが存在しない場合は `gh label create` で作ってから付与する（`revision`, `new-script`）。
- Issue を立てるだけ。台本の編集はこのコマンドでは行わない。
- `CLAUDE.md` の「イシュー駆動ワークフロー」に従う。
