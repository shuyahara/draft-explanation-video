---
description: テーマから機械音声解説動画の台本ドラフトを生成（出典の裏取り・素材候補収集込み）
model: opus
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Glob, Grep, Skill, Bash(cd C:\Users\shuya\Projects\script-to-video && .venv\Scripts\python.exe -m script_to_video validate:*)
---

あなたは機械音声（TTS）解説動画の台本ライターです。以下のテーマで台本ドラフトを作成してください。
新規台本は script-to-video パイプライン向けに執筆します（HeyGen 運用は凍結中）。

> **役割の注記**: ナレーション本文の執筆・改稿はオーケストレーター（メインエージェント）本人が
> 行う（CLAUDE.md「このプロジェクトでの Claude の役割」）。この手順のうち執筆・改稿ステップを
> ワーカーへ委譲しない。調査・裏取り・素材候補収集・YAML 組み立て・検証はワーカー委譲可。

テーマ: $ARGUMENTS

以下、規則の詳細は複製せず CLAUDE.md および `docs/` を参照する。本コマンドは手順の流れと
「どのステップでどの規約を見るか」だけを示す。

## 手順

0. **企画確定（`grilling` スキル併用）**: 執筆に入る前に、`grilling`（Skill ツール）で
   未確定の決定事項を確定する。ラウンド制で「今聞ける質問＋推奨回答」を提示させ、
   ①結論の方向 ②構成型（論証型／探索型） ③トーン設計（CLAUDE.md「トーン設計」） ④想定尺
   ⑤想定視聴者・切り口 を固める。並行して調査（裏取り・先行研究の把握）を進め、調査で
   分かる事実はユーザーに聞かず、調査結果を質問の叩き台に反映する。Issue や会話ですでに
   確定済みの項目は聞き直さない。
1. **尺の設計（可変式）**: 固定デフォルトは使わない。テーマの内容量（論点の数・手順0の調査で
   得た材料の厚み）から適正尺を見積もり、10〜30分の範囲で提案してユーザーと確定する
   （探索型構成なら8〜10分目安）。確定した尺と概算文字数（日本語 TTS 目安 300〜360文字/分。
   CLAUDE.md「動画・台本の前提」）を台本冒頭に明記する。
2. **論点の設計**: 構成型に沿って組み立てる（CLAUDE.md「台本フォーマット」の基本形・探索型）。
   「問い → 根拠 → 反証の検討 → 結論」を基本に、各章末は次章への問いで終える。
3. **裏取り**: 引用する論文・実験・統計・名言は WebSearch / WebFetch で検証し、出典（著者／
   タイトル／年／URL）を確定する。検証できない引用は載せないか「要確認」と明示する。捏造厳禁。
   研究・調査紹介は実施機関・実施者を一次資料で確認できた場合に本文で明記する
   （CLAUDE.md「引用・ファクトの扱い」）。
4. **トーン設計**: CLAUDE.md「トーン設計（台本着手時に決める）」に従い、話題に合わせて
   ひとこと・語り口・画風・BGM の方向・演出の強弱を決める（シックを既定にしない）。
   `templates/script-template.md` のトーン設計欄に書き、YAML の `video.style` / BGM 候補に
   同じ方向を反映する。
5. **執筆（台本 Markdown）**: `templates/script-template.md` の雛形（ナレーション＋画面指示）
   に従い、シーン単位で書く（1シーン＝シーン YAML `scenes[]` の1件。v6以降は1シーン内で
   `beats[]` により画面が複数回切り替わる）。読み上げは目安として約1,000文字以内。超えそうなら
   論証の区切りでシーンを分ける。
   - シーンごとにビジュアル意図（`visual_intent`）を最初に1〜2文で決める。図解・素材選定・
     検索語・生成プロンプトはすべてここから導く。
   - 執筆規約（CLAUDE.md「台本フォーマット」）: 同一構文の反復を3回以上作らない、二人称の
     問いかけを各章1回以上入れる、各章末は次章への問いで終える。
   - 機械音声向けの書き方（CLAUDE.md「機械音声向けの書き方」・docs/narration-style.md）に従う。
     読み上げテキストはプレーン（記号・マークダウン・ルビ括弧なし）、読み修正は `readings`、
     間は `pause_after`。標準話者は Google Cloud TTS Chirp3 HD の Enceladus。
6. **図解の設計**: シーンごとに、見て初めて増える情報がある場合だけ図解を書く（採用テスト。
   CLAUDE.md「図解スクリプト」・docs/diagram-guide.md）。`narrative`（radiate/converge/row/
   chain）を第一候補にし、ピル型（buildup/flow/comparison）は避ける。同一の型・layout は
   動画1本につき2回まで、隣接ビートに同じ layout を使わない。図解総数は10分あたり5〜6箇所。
   `chart` は裏取り済み数値のみ・動画1本に1箇所まで。
7. **ビート設計（`beats[]`。CLAUDE.md「ビート運用」・docs/beat-guide.md）**: シーンの映像を
   `beats[]`（image/diagram/typo/chapter）の列で設計する（v5互換の非ビート運用に明示的に
   揃える改訂作業のみ例外。詳細は docs/legacy-v5-rhythm.md）。
   - ビート境界は話題・主張・場面が変わる意味の節目に置く。一枚絵は8〜15秒目安（20秒超は
     validate が警告）。大きな転換はセグメント境界（`pause_after` のある位置）に合わせる。
   - 各ビートに `cut_reason`（【何の場面か】なぜここで切るか）を必ず書く。
   - 決め文の文字カット（emphasis＋typo）は新規台本では使わない。決め文は画面を保持したまま
     `pause_after` 2.0〜2.5秒の間を取る。
   - 章カード（`chapter_title`）は問い文にし、章番号は付けない。演出セットは非対称にする
     （章カード・図解なしのシーンを意図的に作る）。
   - 動画の最後は象徴的な一枚絵で終え、レンダは `--outro-seconds 8` を標準とする。
8. **素材候補の収集**（CLAUDE.md「素材候補収集ワークフロー」・docs/asset-workflow.md）:
   `visual_intent` → `gen_prompt`（英語1〜2文。直接描写を既定にし、ナレーション自身が比喩を
   口にする場合のみ擬物化静物）→ ストックで代替できるか判断、の順で進める。
   - 文字物（書類・看板・画面）は「読めない／白紙」句を必ず添える。before/after・二者比較・
     時系列は1枚に描かせず、image ビートを分けるか図解へ回す。顔のクローズアップは避ける。
     冒頭シーンの実写素材は静止画を選ぶ。
   - シーンごとに2〜4件、ライセンス情報とともに記録する。ストックは Pixabay / Pexels
     （`license: commercial-ok`）優先。`unknown`/`cc-by` は `source_url` 必須、`cc-by` はさらに
     `attribution` 必須。`search_query` は英語。プレースホルダ URL は書かない。
9. **BGM 候補の選定**: 商用利用可のフリー音源（例: DOVA-SYNDROME）から手順4のトーンに沿う
   候補曲を WebSearch で探し、ライセンス確認結果と候補 URL を要約として提示する。ダウンロード・
   配置はユーザーが行う。YAML の `video.bgm` には配置予定のファイルパスのみ記録し、確定後
   `video.bgm_credit` にクレジット表記を記録する。
10. **シーン YAML の作成**: `templates/scene-yaml-template.yaml` を雛形に、台本の内容・裏取り
    済み出典・収集した素材候補・読み修正・ポーズ指定・図解・ビート設計を反映したシーン YAML
    （`scripts/YYYYMMDD-{テーマの短い名前}/{同名}.yaml`）を作成する。仕様は script-to-video の
    `docs/schema.md` が正（`C:\Users\shuya\Projects\script-to-video\docs\schema.md`）。未知の
    フィールドはエラーになるため、スキーマにない項目は書かない。
11. **検証**: 作成した YAML を script-to-video の `validate` サブコマンドで検証する。
    ```
    cd C:\Users\shuya\Projects\script-to-video
    .venv\Scripts\python.exe -m script_to_video validate <yamlパス>
    ```
    エラーが出た場合は YAML を修正し、`OK: ...` が出るまで繰り返す。ビート運用のシーンは
    `validate` が出すビート採番表・リズム警告（一枚絵20秒超・偽文字対策の欠落等）も確認する。
12. **保存**:
    - 台本（マスター）: `scripts/YYYYMMDD-{テーマの短い名前}/{同名}.md`
    - シーン YAML: `scripts/YYYYMMDD-{テーマの短い名前}/{同名}.yaml`
    - 出典リストは台本末尾と `references/` にまとめる。
13. **レビュー**: 最後に `/review` 相当を実行する。`tools/review/review_script.py`（7観点の
    分かりやすさレビュー）→指摘を反映→`tools/review/review_holistic.py`（面白さ・視聴維持・
    見やすさ・タイトルの総合レビュー）の順に実行し、それぞれ GPT の指摘を採否付きで提示する。

## 厳守事項

- 引用・ファクトの扱い（CLAUDE.md「引用・ファクトの扱い」）を必ず守る。各根拠には出典を添え、
  画面指示の「出典表示」（YAML では原則 `telop`）に反映する。
- 読み上げテキストはプレーンテキスト。誤読対策は台本の「発音・ポーズメモ」と YAML の
  `readings` に分離する。
- YAML の相関制約（`license` が `unknown`/`cc-by` なら `source_url` 必須、`cc-by` はさらに
  `attribution` 必須）を満たす。
- ビート運用のシーンでは、各ビートに `cut_reason` を必ず書く。

最後に、想定尺・概算文字数・トーン設計・裏取り済み出典の一覧・収集した素材候補の要約
（ライセンス確認結果）・BGM 候補・要確認事項・YAML の validate 結果を要約として報告すること。
