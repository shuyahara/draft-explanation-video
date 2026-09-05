# 冷笑 ずんだもん版 アップロード記録（ずんだ人文学 UCzqqrnAzRo_rWPBCXC1yuuw）

| 版 | 動画ID | 状態 | 日付 | メモ |
|---|---|---|---|---|
| v1 | TDTVoyTeEUE | 非公開・処理待ち（29:38） | 2026-09-05 | build/cynicism-kamishibai-v1（実体 D:\script-to-video-build）。台本 v2（Codex セリフレビュー反映）、写真 35 枚、図解 4、話速 1.1、BGM「青空に口笛」、サムネ C（ジェローム「ディオゲネス」）、字幕 ja。概要欄 description-v1.txt |

旧版削除ルール: 修正版をアップロードして処理完了・再生確認後に旧 ID を削除し、この表に「削除済み」と記す（docs/decisions.md 2026-09-01）。

コマンド:
```
cd C:\Users\shuya\Projects\script-to-video
PYTHONUTF8=1 .venv\Scripts\python.exe -m script_to_video upload D:\script-to-video-build\cynicism-kamishibai-v1\cynicism-kamishibai-v1.mp4 --title "なぜ人は冷笑してしまうのか――犬は権力に吠え、冷笑は本気に吠える" --description-file ...\publish\20260905-cynicism-kamishibai\description-v1.txt --tags "冷笑,シニシズム,社会心理学,ディオゲネス,ずんだもん,四国めたん,VOICEVOX,雑学" --privacy private --thumbnail ...\thumb-C.png --srt ...\full.srt --token secrets\youtube_token_kamishibai.json
```
