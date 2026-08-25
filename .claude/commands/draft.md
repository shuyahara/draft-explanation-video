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
   - **各シーンのビジュアル意図を最初に定義する**（CLAUDE.md「ビジュアル意図を最初に書く」）。
     「どんな絵で見せたいか」を1〜2文で決め、台本の「ビジュアル」欄に書く。図解・実写・
     背景付き図解のどれを選ぶか、検索クエリ、生成プロンプトは、すべてこの意図から導く。
   - シーンごとに、CLAUDE.md「図解スクリプト（`diagram`）」の画面構成の決め方に従って
     **全画面実写 / 図解のみ（無地下地） / 背景付き図解** を判定する。論証・手順・比較・データの
     シーンは図解（画面が寂しければ背景付き図解）、情景描写・フック・エピソードは実写。
     全体の3〜5割を図解の目安にする。
   - 図解シーンは型（`buildup` / `flow` / `comparison` / `chart`）を選び、ナレーションのセグメント分割を
     図解の出現粒度に合わせる（「どの文で何が新しく登場するか」の切れ目で分ける。**文の途中では分けない**）。
   - 章（論証の節）が変わるところで `key_color` を設定する（任意。同じ章のシーンには同じ色を書く）。
   - 章の先頭シーンには `chapter_title` を付ける（必要なら `chapter_bgm` も併記）。
   - 各章の決め文には `emphasis` を検討する（**1章に1〜2箇所まで**。付けすぎない）。
5. **ビート設計（v6以降の標準。CLAUDE.md「ビート運用」）**: シーンごとに映像トラックを
   `beats[]` の列として設計する（v5互換を明示的に維持したい改訂作業を除き、新規台本は
   ビート運用を既定とする）。
   - **絵コンテを作る**: シーンのナレーションを字幕キュー（「。！？」区切りの文単位）に
     分け、**話題・主張・場面が変わる意味の節目**でビート境界を決める（字幕キューの機械的な
     1文1カットにしない）。同じ話題を掘り下げている間は1枚に保持し、一枚絵は**8〜15秒を
     目安**にする（20秒を超えそうならもう1枚に分けるか図解を挟む）。**大きな転換（章の
     変わり目・場面転換）はセグメント境界（`pause_after` のある位置）に合わせる**。
   - 各ビートに `type`（`image` / `diagram` / `typo` / `chapter`）を割り当てる。
     - `image`: 一枚絵。`motion` は原則省略（既定 `parallax`。方向はツールが自動割り当て）。
       意味がある時だけ明示する（収束・集中＝`parallax_in`、広がり・並び＝
       `parallax_left`/`parallax_right`、平面的な画＝`zoom_in`/`zoom_out`）。
     - `diagram`: 図解。**`narrative`（`layout: radiate`/`converge`/`row`）を第一候補**にする
       （旧来のピル型 `buildup`/`flow`/`comparison` は `chart` を除いてビート運用では
       非推奨）。要素の `at` は**字幕キュー番号**（非ビート運用のセグメント番号とは異なる）。
     - `typo` / `chapter`: 文言を持たない。それぞれ `emphasis[].at` / `chapter_title` と
       `at` や先頭ビートの位置で対応づけるだけ（文言・尺の正本は `emphasis` / `chapter_title`
       のまま）。
   - **各ビートに `cut_reason`（ここで画を切り替える意味的な理由）を必ず書く**。
     「【何が起きる場面か】なぜここで束ねる／切るか」の一言でよい（レンダリングには使われず
     `validate` とギャラリーが表示するだけだが、後から転換の速さを見直す唯一の手がかりになる）。
   - `beats` を使うシーンでは、シーン直下に `assets` / `gen_prompt` / `search_query` /
     `diagram` / `diagrams` / `cutaways` を書かない（エラーになる。すべて対応するビートが持つ）。
     一部区間だけに被せるインサートを表現したい場合は `image` ビートを分ける。
6. **素材候補の収集**: シーンごとに、シーン YAML の `assets`（非ビート運用）または各 `image`/
   `diagram` ビート（ビート運用）に記録する候補素材を実際に検索して集める。
   - **説明イラストは「説明イラスト第一」で考える**（CLAUDE.md「素材候補収集ワークフロー」）。
     ①`visual_intent` を決める → ②その情景の `gen_prompt` を必ず起草する（英語1〜2文。
     連結順は `gen_prompt` が先・`video.style` が後。文字物を描く場合は偽文字対策の句を必ず
     添える）→ ③ストックで代替できるか判断する（代替できるならストック優先、できなければ
     `gen_prompt` を第一候補のまま残す）。`cutaways`（非ビート運用）や `image`/`diagram`
     ビート（ビート運用）のスロットも同じ手順で `visual_intent` / `gen_prompt` /
     `search_query` / `assets` を用意する。
   - **全画面実写**のシーンと、**背景付き図解**にすると判定したシーンで候補を集める
     （`diagram` と `assets` の併記は背景付き図解として解釈される。排他ではない）。
   - **図解のみ（無地下地）**にしたシーンは `assets` を書かない。
   - シーンごとに **2〜4件**、ライセンス情報とともに記録する。
   - ストック素材は **Pixabay / Pexels**（商用利用可・クレジット不要）を優先して WebSearch で探す。`license: commercial-ok`。
   - Wikimedia Commons の候補は PD か CC-BY かを確認する。CC-BY の場合は出典表記文字列を `attribution` に記録する（`source_url` と `attribution` が必須）。
   - ライセンス不明（汎用画像検索由来）の候補は `license: unknown` とし、`source_url` を必ず記録する（権利要確認）。
   - 存命人物が写る候補には、肖像権・パブリシティ権の注意を `note` に付記する。
   - `search_query` は **英語** で書く（Pixabay / Pexels / Commons の検索に渡すため）。
   - プレースホルダの URL は書かない。必ず WebSearch / WebFetch で実在を確認したものだけを記録する。
7. **BGM 候補の選定**: 商用利用可のフリー音源（例: DOVA-SYNDROME）から候補曲を WebSearch で探し、
   ライセンス確認結果と候補 URL を要約として提示する。ダウンロード・配置はユーザーが行うため、
   YAML の `video.bgm` には（配置予定の）ファイルパスのみ記録する。BGM をユーザーと確定できたら、
   クレジット表記文字列を `video.bgm_credit` に記録する。
8. **シーン YAML の作成**: `templates/scene-yaml-template.yaml` を雛形に、台本の内容・裏取り済み出典・
   収集した素材候補・読み修正・ポーズ指定・図解スクリプト・ビート設計を反映したシーン YAML
   （`scripts/YYYYMMDD-{テーマの短い名前}/{同名}.yaml`）を作成する。
   - 各シーンの `visual_intent` に、手順4で決めたビジュアル意図をそのまま書く。
   - 仕様は script-to-video の `docs/schema.md` が正（`C:\Users\shuya\Projects\script-to-video\docs\schema.md`）。
     未知のフィールドはエラーになるため、スキーマにない項目は書かない。
   - 誤読しやすい語は `readings`（`surface` / `reading`）に記録する。
   - 間を入れたい箇所は `narration` をセグメント分割し、直前のセグメントに `pause_after`（秒）を付ける。
   - **ビート運用のシーン**は手順5で設計した `beats[]`（`type`・`cut_reason`・`from`/`at`・
     `slot`・`motion`・`diagram`）をそのまま書く（`templates/scene-yaml-template.yaml` の
     id: 9 を参照）。図解ビートは手順5で選んだ型（`narrative` 第一候補）に沿って書き、
     CLAUDE.md「図解スクリプト」のチェックリストを守る（ラベル12文字以内・座標や
     アニメーションの数値は書かない）。`chapter_title`/`emphasis` は従来どおりシーン直下に
     書き、対応する `chapter`/`typo` ビートを添える。シーン直下に `assets` /
     `gen_prompt` / `search_query` / `diagram` / `diagrams` / `cutaways` は書かない。
   - **非ビート運用のシーン**（v5互換の改訂作業など）は、図解シーンを手順4で判定した型に
     沿って `diagram` を書き、`chapter_title`（＋必要なら `chapter_bgm` / `chapter_bgm_credit`）・
     `emphasis`・`cutaways`・複数図解が必要なシーンは `diagram` の代わりに `diagrams` を
     反映する（CLAUDE.md「映像リズムの設計」）。
9. **検証**: 作成した YAML を script-to-video の `validate` サブコマンドで検証する。
   ```
   cd C:\Users\shuya\Projects\script-to-video
   .venv\Scripts\python.exe -m script_to_video validate <yamlパス>
   ```
   エラーが出た場合は YAML を修正し、`OK: ...` が出るまで繰り返す。ビート運用のシーンは
   `validate` が出すビート採番表・リズム警告（一枚絵20秒超・偽文字対策の欠落等）も確認する。
10. **保存**:
   - 台本（マスター）: `scripts/YYYYMMDD-{テーマの短い名前}/{同名}.md`
   - シーン YAML: `scripts/YYYYMMDD-{テーマの短い名前}/{同名}.yaml`
   - 出典リストは台本末尾と `references/` にまとめる。

## 厳守事項

- `CLAUDE.md` の「引用・ファクトの扱い」「機械音声向けの書き方（VOICEVOX 前提）」「script-to-video 向け出力」を必ず守る。
- 各根拠には出典を添え、画面指示の「出典表示」（YAML では原則 `telop`）に反映する。
- **読み上げテキストはプレーンテキスト**。記号・マークダウン・ルビ括弧（例: `API（エーピーアイ）`）は入れない。
  誤読対策は台本の「発音・ポーズメモ」と YAML の `readings` に分離する。
- YAML の相関制約を満たす（`license` が `unknown` または `cc-by` の場合 `source_url` 必須、
  `cc-by` の場合はさらに `attribution` 必須）。
- **ビート運用のシーンでは、各ビートに `cut_reason`（切り替えの意味的な理由）を必ず書く**
  （レンダリングには使われないが、書かれないことを避けるため必須。CLAUDE.md「ビート運用」）。

最後に、想定尺・概算文字数・裏取り済み出典の一覧・収集した素材候補の要約（ライセンス確認結果）・
BGM 候補・要確認事項・YAML の validate 結果を要約として報告すること。
