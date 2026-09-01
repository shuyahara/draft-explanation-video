# タイトル候補（なぜ人は冷笑してしまうのか）

1. なぜ人は冷笑してしまうのか（台本の問いそのまま）
2. なぜ人は冷笑してしまうのか ― 犬は権力に吠え、冷笑は本気に吠える【推奨】
3. 冷笑は安い。だが後で高くつく ― 人はなぜ本気を嗤うのか
4. 「意識高いね」と笑う人の心理 ― 冷笑の2400年史
5. 冷笑する人ほど損をする？ ― 心理学が示す「安い知性」の請求書

推奨は案2。検索語（冷笑）が先頭に入り、動画の決め文（章1の結び）をサブに置くことで
「古代→現代」の軸が伝わる。案3は結論先出しのクリック率重視、案4は日常語で入口を広げる案。
案5は数字・損得を前に出す案だが、動画のトーン（静かな考察）からは少し外れる。

## 公開物
- 概要欄: `description.txt`（チャプター時刻は v6 のレンダ結果で最終確認）
- サムネイル候補: `thumbnails.md`

## アップロード記録（2026-08-28）
- YouTube 非公開ドラフト: https://youtu.be/zXm8CSf61T0（動画ID zXm8CSf61T0）
- 本編: `script-to-video/build/cynicism-v6-codex/cynicism-v6-codex.mp4`（20:20、−14.2 LUFS）
- タイトル: 案2「なぜ人は冷笑してしまうのか ― 犬は権力に吠え、冷笑は本気に吠える」（仮）
- サムネイル: thumb-A.png（文言「なぜ冷笑してしまうのか？」3 行版。2026-08-28 ユーザー確定、thumbnails.set 済み）／字幕: full.srt（ja）／概要欄: description.txt（チャプター時刻は v6 timeline 準拠）
- 公開は YouTube Studio で手動（API 未審査のため強制非公開）。タイトル・サムネの変更があれば差し替える。

## v7 再アップロード（2026-08-28）
- **v7（公開版候補）**: https://youtu.be/sWA35PY2rgg（動画ID sWA35PY2rgg。20:36、−14.2 LUFS。誤読 3 語修正・章 2/3 タイトル変更・GPT 最終レビュー採用 13 件を反映）
- 旧 v6（zXm8CSf61T0）は削除対象（YouTube Studio で削除。API 削除は行っていない）
- ショート: 短1 / 短2 を別途アップロード（下記）
- 短1（本編圧縮版）: https://youtu.be/Av1y838DlUk（タイトル「なぜ人は冷笑してしまうのか ― 冷笑は安い。だが後で高くつく #Shorts」、サムネ short1-thumb.png）
- 短2（犬と冷笑の反転）: https://youtu.be/_omOK5qlinQ（タイトル「犬は権力に吠え、冷笑は本気に吠える ― シニシズムの語源 #Shorts」、サムネ short2-thumb.png）
- ショートの概要欄には本編 URL（sWA35PY2rgg）を記載済み。本編公開後も ID は不変。

## v8 再アップロード（2026-08-29）
- **v8（公開版候補）**: https://youtu.be/g4CIjYTNB_Y（動画ID g4CIjYTNB_Y。20:44、−14.2 LUFS。シーン 4 キュー 16〜19 の橋渡し（主語・目的語を補う）を反映。チャプター 0:00 / 1:23 / 5:23 / 7:47 / 13:14）
- 旧 v7（sWA35PY2rgg）・v6（zXm8CSf61T0）は削除対象。
- ショート 2 本の概要欄の本編 URL を g4CIjYTNB_Y に更新（API で videos.update 済み）。

## 未完了（2026-08-29）
- 短1 改稿版（`script-to-video/build/cynicism-short1/short.mp4`、62.0 秒）の YouTube アップロードは **OAuth トークン失効（テストモード 7 日）** のため保留。次回、在宅時にブラウザ認可のうえ実行する:
  `python -m script_to_video upload "build/cynicism-short1/short.mp4" --title "なぜ人は冷笑してしまうのか #Shorts" --description-file ".../publish/20260827-cynicism/short1-description.txt" --tags "冷笑,シニシズム,社会心理学,Shorts" --privacy private --thumbnail ".../publish/20260827-cynicism/short1-thumb.png"`
- 成功後: 旧短1（Av1y838DlUk）を削除、本記録に新 ID を追記。

## 短1 改稿版アップロード（2026-09-01）
- 新短1: https://youtu.be/MiADYaUL2ec（62.0秒・cue4差し替え済み改稿版。サムネ short1-thumb.png 設定済み・非公開）
- 旧短1（Av1y838DlUk）は新IDの再生確認後に削除する（削除運用: docs/decisions.md 2026-09-01。API削除は自動モードでブロックされたため Studio での削除または権限許可が必要）
