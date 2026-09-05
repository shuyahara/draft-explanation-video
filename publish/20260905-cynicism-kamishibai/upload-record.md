# 冷笑 ずんだもん版 アップロード記録（ずんだ人文学 UCzqqrnAzRo_rWPBCXC1yuuw）

| 版 | 動画ID | 状態 | 日付 | メモ |
|---|---|---|---|---|
| v1 | TDTVoyTeEUE | **削除済み（2026-09-05、v2 処理完了後）** | 2026-09-05 | build/cynicism-kamishibai-v1（実体 D:\script-to-video-build）。台本 v2（Codex セリフレビュー反映）、写真 35 枚、図解 4、話速 1.1、BGM「青空に口笛」、サムネ C（ジェローム「ディオゲネス」）、字幕 ja。概要欄 description-v1.txt |
| v2 | BeotcrzVwEk | **削除済み（2026-09-05、v4 処理完了後）** | 2026-09-05 | build/cynicism-kamishibai-v2。台本 v4（冒頭を有名人のボランティア投稿→売名に変更、レビュー一式＝7観点・総合・セリフ×2・つなぎ・間を反映、S4 radiate 図解、S12 章カード追加）。サムネ C、字幕 ja。概要欄 description-v2.txt。既知の軽微な不具合: S4 テロップの「1983–84」のダッシュが□表示（修正は次レンダで） |
| v3 | kERO4v0oSLc | **削除済み（2026-09-05）**。「無力感」の読みが直っていなかった（辞書 priority 5 で負け） | 2026-09-05 | build/cynicism-kamishibai-v3。S4 テロップのダッシュは修正済み |
| v4 | v-8HlXEvNOE | 非公開（31:10）→ v5 処理完了後に削除 | 2026-09-05 | build/cynicism-kamishibai-v4。v3 ＋ 「無力感→ムリョクカン」（VOICEVOX 辞書 priority 10、tts.py 修正）。ASR で読みを確認済み。概要欄 description-v3.txt（章 8 件）、サムネ C、字幕 ja |
| v5 | l7c9CdMUNbk | **非公開・試写用（31:15）** | 2026-09-05 | build/cynicism-kamishibai-v5。ユーザー編集（S1 口語化・S4 突き上げ／行動）、S3 前振り・S4 反論→質問（ユーザー指摘）、ジジェク削除（判断 B）、結び「次の投稿に行く前に止まれた」、放射図解の 3 項目目を 19 世紀の語義に。概要欄 description-v4.txt（章 8 件）、サムネ C、字幕 ja |

旧版削除ルール: 修正版をアップロードして処理完了・再生確認後に旧 ID を削除し、この表に「削除済み」と記す（docs/decisions.md 2026-09-01）。

コマンド:
```
cd C:\Users\shuya\Projects\script-to-video
PYTHONUTF8=1 .venv\Scripts\python.exe -m script_to_video upload D:\script-to-video-build\cynicism-kamishibai-v1\cynicism-kamishibai-v1.mp4 --title "なぜ人は冷笑してしまうのか――犬は権力に吠え、冷笑は本気に吠える" --description-file ...\publish\20260905-cynicism-kamishibai\description-v1.txt --tags "冷笑,シニシズム,社会心理学,ディオゲネス,ずんだもん,四国めたん,VOICEVOX,雑学" --privacy private --thumbnail ...\thumb-C.png --srt ...\full.srt --token secrets\youtube_token_kamishibai.json
```
