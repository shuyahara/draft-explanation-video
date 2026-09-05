---
description: 別モデル（GPT。Codex CLI 経由）による自動レビューを実行し、指摘の採否を判断して反映する
allowed-tools: Bash(PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" tools/review/*:*), Read, Edit, Glob, Grep, Bash(cd C:\Users\shuya\Projects\script-to-video && .venv\Scripts\python.exe -m script_to_video validate:*)
---

引数: `{台本mdパス or scriptsフォルダ} [--video <レンダ出力dir>]`

依頼内容: $ARGUMENTS

台本リポジトリのナレーション・映像を、別モデル（GPT。Codex CLI 経由）に自動レビューさせる。
**①台本レビュー**（`tools/review/review_script.py`）→**②総合レビュー**
（`tools/review/review_holistic.py`。面白さ・視聴維持・見やすさ・タイトル）に加え、`--video`
指定時のみ実行する**③映像レビュー**（`tools/review/review_video.py`）。対象が**対話台本
（めたん×ずんだもん紙芝居版）**の場合は、これに加えて対話専用のレビュー一式（手順5）も回す。
詳細は `tools/review/README.md`。

## 手順

1. **対象の特定**: 引数が `scripts/` 配下のフォルダなら、その中の台本 md（フォルダと同名の
   `.md`）を対象とする。台本 md へのパスが直接渡された場合はそれをそのまま使う。あわせて、
   台本 md 内に発話行 `**話者**（表情）: 本文`（例: `**ずんだもん**（confused）: ...`）が
   あるかを確認し、あれば**対話台本（めたん×ずんだもん紙芝居版）**と判別する（手順5の対象）。
2. **台本レビュー**: 以下を実行する（1回2〜3分程度）。
   ```
   cd C:\Users\shuya\Projects\draft-explanation-video
   PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
       tools/review/review_script.py <台本mdパス>
   ```
   出力先（`references/{実行日}-{台本フォルダ名}-gptreview.md`）を読む。
3. **総合レビュー**（面白さ・視聴維持・見やすさ・タイトル）: 7観点レビュー（手順2）の指摘を
   反映した後の台本に対して実行するのが望ましい。
   ```
   PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
       tools/review/review_holistic.py <台本mdパス>
   ```
   出力先（`references/{実行日}-{台本フォルダ名}-holistic.md`）を読む。
4. **映像レビュー**（`--video <レンダ出力dir>` が指定されたときのみ）: 台本と同じフォルダにある
   シーン YAML を対象に実行する。
   ```
   PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
       tools/review/review_video.py <YAMLパス> <レンダ出力dir>
   ```
   動画1本フルで回すと時間がかかるため、シーン数が多い場合は `--scenes` で分割して実行してよい。
   出力（`<レンダ出力dir>/review/video-review.md`）を読む。
   **読み上げレビュー**（同じく `--video` 時。TTS の誤読候補）: `tools/review/review_reading.py --yaml <YAMLパス> --audio-dir <TTS 出力dir> --out references/{実行日}-{台本フォルダ名}-reading-check.md` を実行する（faster-whisper で文字起こし→かな化して台本と比較。約 5 分/20 分動画。要確認は候補なので該当音声を聴いて判断する）。
   **ショート動画の場合**: `--video` 指定時、`tools/review/review_short.py` でキュー単位の GPT 検品も回す（通常尺の映像レビューとは別に、ショート特有の短尺キュー構成を検品する）。
5. **対話台本専用レビュー**（手順1で対話台本と判別した場合のみ）: `review_dialogue.py`（セリフ）
   →`review_transitions.py`（章のつなぎ）の順で実行する。
   ```
   PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
       tools/review/review_dialogue.py <台本mdパス>
   PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
       tools/review/review_transitions.py <台本mdパス>
   ```
   出力先（`references/{実行日}-{台本フォルダ名}-dialogue-review.md` /
   `references/{実行日}-{台本フォルダ名}-transitions-review.md`）を読む。
   台本をシーン YAML 化した後（`tools/kamishibai_md_to_yaml.py` 実行後）は、`pause_after` の
   間・息継ぎレビューも回す。
   ```
   PYTHONUTF8=1 "C:/Users/shuya/Projects/script-to-video/.venv/Scripts/python.exe" ^
       tools/review/review_pauses.py <シーンYAMLパス>
   ```
   出力先（`references/{実行日}-{台本フォルダ名}-pause-review.md`）を読む。話速が 1.0 の台本
   （旧 VOICEVOX 等速）では `--tempo 1.0` を付ける。
6. **採否の提示**: ここまでの各レビューの指摘を1件ずつ検討し、
   各指摘に**「採用／不採用／要判断」と根拠**を付けてユーザーに提示する。判断基準:
   - 事実誤認・論理の飛躍・誤帰属につながる指摘は原則採用。
   - 語り口・演出上の意図的な選択（CLAUDE.md「トーン設計」「章の設計」に基づく反復・比喩等）を
     壊す指摘は不採用でよい。理由を明記する。
   - 「決定論チェック」の指摘は、ツールが単純な文字列マッチ・秒数比較で出しているだけなので、
     実際に問題かどうかは文脈で判断する（`tools/review/README.md` の「決定論チェック」節を参照）。
     テロップの指摘は区分A「ナレーションにない文字」（捏造検出。原則採用）と区分B「字幕の写し」
     （ナレーションと同じ文言をそのまま表示しているだけの疑い。問いの強調表示など意図的な場合も
     あるため要判断）に分かれる。テロップ再出現・20秒超ビートも同様に文脈で判断する。
7. **反映**: 採用した指摘を、台本フォーマット規約（CLAUDE.md「台本フォーマット」「引用・ファクトの
   扱い」「機械音声向けの書き方」。対話台本は加えて `docs/dialogue-guide.md`）に従って
   ナレーション（md）と対応する YAML に反映する（ナレーション本文の執筆・改稿はオーケストレーター
   自身が行う。CLAUDE.md「このプロジェクトでの Claude の役割」）。
8. **再検証**: 反映後、YAML を `validate` サブコマンドで再検証する。
   ```
   cd C:\Users\shuya\Projects\script-to-video
   .venv\Scripts\python.exe -m script_to_video validate <yamlパス>
   ```
   `OK: ...` が出るまで修正を繰り返す。

## 注意

- `review_script.py` / `review_holistic.py` / `review_video.py` / `review_dialogue.py` /
  `review_transitions.py` / `review_pauses.py` は**指摘を生成するだけ**で、台本・YAML の
  文言は一切編集しない。編集は本コマンドの手順7でオーケストレーターが行う。
- Codex CLI のクォータ超過（「usage limit」「at capacity」等）で失敗した場合は、ツール側が
  60秒待って1回だけ自動再試行する。それでも失敗したら少し時間を置いて再実行を提案する。
- Issue 起点の作業（`#N`）なら、採否の判断根拠と反映内容を `gh issue comment` で記録する
  （CLAUDE.md「イシュー駆動ワークフロー」）。
