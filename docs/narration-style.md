本書は CLAUDE.md から 2026-08-26 に切り出した参照資料（Issue #15）。規則の正本は CLAUDE.md、
本書は機械音声向けの書き方の詳細（ポーズ設計の目安・実測値・根拠文献・クレジット）。

## 機械音声向けの書き方（詳細）

話者は **Google Cloud TTS Chirp3 HD の Enceladus**（落ち着いた男性声）を標準とする
（2026-08-26 採用。聴き比べの経緯は ../references/ の TTS 調査メモと Issue #14 参照。
レンダは `--tts-backend gcp --tts-voice ja-JP-Chirp3-HD-Enceladus`、API キーは
script-to-video の `secrets/gcp_tts_api_key.txt`。旧標準の VOICEVOX 青山龍星は
凍結中の過去台本（v6 以前）の背景情報として残す）。台本のナレーションは、シーン YAML の
`narration` セグメントとして機械可読に記録する（詳細は後述「script-to-video 向け出力」）。

- **読み上げテキストはプレーンに**。記号・マークダウン・ルビ括弧は入れない
  （そのまま読み上げられるため）。
- **読み修正**は YAML の `readings`（`surface`＝表記／`reading`＝カタカナ）で機械可読に指定する。
  誤読しやすい語は、台本本文・「発音・ポーズメモ」にも読みをメモしつつ、シーン YAML に
  必ず `readings` エントリを添える。
- **ポーズ（間）**は `narration` セグメントの `pause_after`（秒、機械可読な数値）で指定する。
  間を入れたい箇所でナレーションをセグメント分割し、直前のセグメントに `pause_after` を付ける
  （省略時はポーズなし。台本の「発音・ポーズメモ」にも入れたい箇所を書いておく）。
  **3段階以上を使い分ける**（全箇所を同じ長さにしない）。目安: 短い区切り 0.3〜0.5秒／
  論点の切れ目 0.6〜0.9秒／決め文（言い切り）の直後 1.0〜1.2秒。
  **`pause_after` 省略時のセグメント境界には、エンジンの前後無音マージン由来の短い間
  （VOICEVOX 実測で約0.26〜0.29秒）しか入らない**（VOICEVOX 側のパラグラフ内句読点ポーズ
  〔`pause_scale` が効く〕とは別物で、こちらは常に短い。GCP TTS でもセグメント分割合成＋連結
  という構造は同じ）。文境界でセグメントを分割する場合は、単なる文の連続で間を詰めたい
  ときでも `pause_after` を省略せず、最低 0.2 秒程度を明示する（実測で約0.45〜0.5秒になり、
  「間が短い」と感じられる水準を避けられる。R20 の文間無音実測で判明。
  ../references/20260820-narration-gap-fix.md 参照）。
- **二人称の問いかけを各章1回以上入れる**（例:「あなたは〜と感じたことはないだろうか」）。
  会話体・二人称での語りかけが学習効果を高めるという Mayer のパーソナライゼーション原理を
  根拠とする（Moreno, R., & Mayer, R. E. (2000). Engaging students in active learning: The
  case for personalized multimedia messages. *Journal of Educational Psychology*, 92(4),
  724–733.；総説として Mayer, R. E. (2009). *Multimedia Learning* (2nd ed.), Cambridge
  University Press）。ただし「各章1回以上」という頻度自体は本規約側の設計判断であり、
  原論文が定める基準ではない。
- **クレジット表記**: GCP TTS（Enceladus）はクレジット表記不要（script-to-video が
  description.txt に「ナレーション: Google Cloud Text-to-Speech」相当の記載を出す運用。
  動画内エンドクレジットは挿入しない）。旧 VOICEVOX 台本では「VOICEVOX:青山龍星」が
  自動挿入されていた（過去台本の背景情報）。
- 1文を長くしすぎない。句読点で TTS の間（ま）を設計する。
- 同音異義語で誤解が生じる表現は避け、文脈で一意に読めるようにする。
- 視覚に依存する表現（「左の図」「赤い線」等）はナレーション単体で意味が通るよう補う。
- 箇条書きや記号は画面指示側（YAML では `telop`）へ。ナレーションは「話し言葉として自然な
  地の文」にする。

## 話速 1.1 倍のときの間の設計（2026-09-03 試写FB）

- 話速は `--tts-rate 1.1`（GCP speakingRate）を標準にする。speakingRate は読点・文中の息継ぎも約9%縮めるが、`pause_after` の無音は縮まない（GCP では VOICEVOX 用の `pause_scale` は無効）。
- そのため `pause_after` の目安を等速時より一段上げる: 文境界の既定 0.2 → 0.35、段落・話題の区切り 0.8〜1.0、決め文 2.5〜3.0、章転換 1.8〜2.0、二人称の問いかけの後は 1.0 以上。
- 試写で「まだ短い」場合は、script-to-video に `pause_after` の一括倍率オプションを追加する（未実装の案）。
