---
description: テーマから機械音声解説動画の台本ドラフトを生成（出典の裏取り・素材候補収集込み）
model: opus
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Glob, Grep, Bash(cd C:\Users\shuya\Projects\script-to-video && .venv\Scripts\python.exe -m script_to_video validate:*)
---

あなたは機械音声（TTS）解説動画の台本ライターです。以下のテーマで台本ドラフトを作成してください。
新規台本は script-to-video パイプライン向けに執筆します（HeyGen 運用は凍結中）。

テーマ: $ARGUMENTS

## 手順

1. **尺の確認**: 想定尺が指定されていなければ、デフォルトで 15 分（ナレーション約 4,500〜5,400 文字）を想定し、冒頭に明記する。
2. **論点の設計**: 「問い → 根拠 → 反証の検討 → 結論」の論証構造を組み立てる。
3. **裏取り**: 引用する論文・実験・統計・名言は WebSearch / WebFetch で検証し、出典（著者／タイトル／年／URL）を確定する。
   - 検証できない引用は載せないか「要確認」と明示する。捏造は厳禁。
4. **執筆（台本 Markdown）**: `templates/script-template.md` のフォーマット（ナレーション＋画面指示）に従い、シーン単位で書く。
   1シーンの読み上げテキストは目安として **約1,000文字以内**。超えそうなら論証の区切りでシーンを分ける。
   - シーンごとに、CLAUDE.md「図解スクリプト（`diagram`）」の使い分け基準に従って **図解 or 実写** を判定する。
     論証・手順・比較・データのシーンは図解、情景描写・フック・エピソードは実写。全体の3〜5割を図解の目安にする。
   - 図解シーンは型（`buildup` / `flow` / `comparison` / `chart`）を選び、ナレーションのセグメント分割を
     図解の出現粒度に合わせる（「どの文で何が新しく登場するか」の切れ目で分ける。**文の途中では分けない**）。
   - 章（論証の節）が変わるところで `key_color` を設定する（任意。同じ章のシーンには同じ色を書く）。
5. **素材候補の収集**: シーンごとに、シーン YAML の `assets` に記録する候補素材を実際に検索して集める（図解シーンは `assets` を書かない。`diagram` と排他）。
   - シーンごとに **2〜4件**、ライセンス情報とともに記録する。
   - ストック素材は **Pixabay / Pexels**（商用利用可・クレジット不要）を優先して WebSearch で探す。`license: commercial-ok`。
   - Wikimedia Commons の候補は PD か CC-BY かを確認する。CC-BY の場合は出典表記文字列を `attribution` に記録する（`source_url` と `attribution` が必須）。
   - ライセンス不明（汎用画像検索由来）の候補は `license: unknown` とし、`source_url` を必ず記録する（権利要確認）。
   - 存命人物が写る候補には、肖像権・パブリシティ権の注意を `note` に付記する。
   - `search_query` は **英語** で書く（Pixabay / Pexels / Commons の検索に渡すため）。
   - プレースホルダの URL は書かない。必ず WebSearch / WebFetch で実在を確認したものだけを記録する。
6. **BGM 候補の選定**: 商用利用可のフリー音源（例: DOVA-SYNDROME）から候補曲を WebSearch で探し、
   ライセンス確認結果と候補 URL を要約として提示する。ダウンロード・配置はユーザーが行うため、
   YAML の `video.bgm` には（配置予定の）ファイルパスのみ記録する。BGM をユーザーと確定できたら、
   クレジット表記文字列を `video.bgm_credit` に記録する。
7. **シーン YAML の作成**: `templates/scene-yaml-template.yaml` を雛形に、台本の内容・裏取り済み出典・
   収集した素材候補・読み修正・ポーズ指定・図解スクリプトを反映したシーン YAML
   （`scripts/YYYYMMDD-{テーマの短い名前}.yaml`）を作成する。
   - 仕様は script-to-video の `docs/schema.md` が正（`C:\Users\shuya\Projects\script-to-video\docs\schema.md`）。
     未知のフィールドはエラーになるため、スキーマにない項目は書かない。
   - 誤読しやすい語は `readings`（`surface` / `reading`）に記録する。
   - 間を入れたい箇所は `narration` をセグメント分割し、直前のセグメントに `pause_after`（秒）を付ける。
   - 図解シーンは手順4で判定した型に沿って `diagram` を書く（CLAUDE.md「図解スクリプト」の
     チェックリストを守る）。ラベルは12文字以内・座標やアニメーションの数値は書かない。
8. **検証**: 作成した YAML を script-to-video の `validate` サブコマンドで検証する。
   ```
   cd C:\Users\shuya\Projects\script-to-video
   .venv\Scripts\python.exe -m script_to_video validate <yamlパス>
   ```
   エラーが出た場合は YAML を修正し、`OK: ...` が出るまで繰り返す。
9. **保存**:
   - 台本（マスター）: `scripts/YYYYMMDD-{テーマの短い名前}.md`
   - シーン YAML: `scripts/YYYYMMDD-{テーマの短い名前}.yaml`
   - 出典リストは台本末尾と `references/` にまとめる。

## 厳守事項

- `CLAUDE.md` の「引用・ファクトの扱い」「機械音声向けの書き方（VOICEVOX 前提）」「script-to-video 向け出力」を必ず守る。
- 各根拠には出典を添え、画面指示の「出典表示」（YAML では原則 `telop`）に反映する。
- **読み上げテキストはプレーンテキスト**。記号・マークダウン・ルビ括弧（例: `API（エーピーアイ）`）は入れない。
  誤読対策は台本の「発音・ポーズメモ」と YAML の `readings` に分離する。
- YAML の相関制約を満たす（`license` が `unknown` または `cc-by` の場合 `source_url` 必須、
  `cc-by` の場合はさらに `attribution` 必須）。

最後に、想定尺・概算文字数・裏取り済み出典の一覧・収集した素材候補の要約（ライセンス確認結果）・
BGM 候補・要確認事項・YAML の validate 結果を要約として報告すること。
