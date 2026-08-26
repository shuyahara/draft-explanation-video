本書は CLAUDE.md から 2026-08-26 に切り出した参照資料（Issue #15）。規則の正本は CLAUDE.md、
本書は凍結中の HeyGen 運用に関する背景情報・過去台本参照用の詳細。

## 運用の凍結と背景

> **HeyGen 運用は凍結（2026-08-14）**。新規台本は自作レンダリングツール
> [script-to-video](https://github.com/shuyahara/script-to-video) 向けに執筆する。
> 詳細は後述「script-to-video 向け出力」。
>
> **凍結中の旧運用**: 台本は HeyGen（AI Studio / Creator プラン・手動運用）に流し込み、
> AI アバター＋機械音声で読み上げていた（API は使わず、Web エディタへのシーン単位貼り付け／
> CSV 一括インポート）。過去台本（`scripts/` 内の HeyGen 期のもの）の背景として、
> HeyGen 関連の記述は本ドキュメントに簡潔に残す。

## 読み上げ文の文字数上限の由来

読み上げ文は目安として **約1,000文字以内**（旧 HeyGen 運用のセグメント上限に由来する目安だが、
シーンの粒度として引き続き有効なため維持する。長くなる場合は論証の区切りでシーンを分ける）。

## 旧標準の音声・クレジット表記（VOICEVOX 青山龍星）

話者は **Google Cloud TTS Chirp3 HD の Enceladus**（落ち着いた男性声）を標準とする
（2026-08-26 採用。聴き比べの経緯は ../references/ の TTS 調査メモと Issue #14 参照。
レンダは `--tts-backend gcp --tts-voice ja-JP-Chirp3-HD-Enceladus`、API キーは
script-to-video の `secrets/gcp_tts_api_key.txt`。旧標準の VOICEVOX 青山龍星は
凍結中の過去台本（v6 以前）の背景情報として残す）。台本のナレーションは、シーン YAML の
`narration` セグメントとして機械可読に記録する（詳細は後述「script-to-video 向け出力」）。

- **クレジット表記**: GCP TTS（Enceladus）はクレジット表記不要（script-to-video が
  description.txt に「ナレーション: Google Cloud Text-to-Speech」相当の記載を出す運用。
  動画内エンドクレジットは挿入しない）。旧 VOICEVOX 台本では「VOICEVOX:青山龍星」が
  自動挿入されていた（過去台本の背景情報）。

## 読み・ポーズ調整（HeyGen 前提）

> **凍結中の旧運用（HeyGen 前提）**: HeyGen はスクリプト欄の文字をそのまま読み上げるため、
> `API（エーピーアイ）` のようなルビ括弧は不可だった（括弧の中身まで読まれる）。読み調整は
> 単語を右クリックする「発音（Pronunciation）」機能、ポーズは Pause ボタン（0.5秒刻み）で
> 行っていた。過去台本（HeyGen 期のもの）を参照する際の背景情報として残す。

## シーンテーブル CSV（HeyGen 前提）

> **凍結中の旧運用（HeyGen 前提）**: 運用は AI Studio（Web手動・Creator プラン）。API は使わず、
> 台本（Markdown）をマスターとし、HeyGen に流し込む **シーンテーブル CSV**
> （`scripts/{台本と同名}.heygen.csv`。列: `scene, 読み上げテキスト, テロップ, ビジュアル素材,
> 発音ポーズメモ`。雛形 `../templates/heygen-scenes.csv`）を併せて出力していた。
> 過去台本（HeyGen 期のもの）を参照する際の背景情報として残す。

## ディレクトリ構成での言及

- 凍結中の HeyGen 期の台本には、代わりに取り込み用 CSV（`{同名}.heygen.csv`）が付随する。
- `../templates/` 配下には凍結中の HeyGen 用 CSV 雛形（`heygen-scenes.csv`）も
  過去台本参照用に残置する。
