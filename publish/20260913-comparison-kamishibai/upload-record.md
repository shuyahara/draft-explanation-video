# アップロード記録: 人はなぜ他人と比べてしまうのか ― 比べるのをやめられない本当の理由（紙芝居版）

チャンネル: ずんだ人文学。トークン `script-to-video/secrets/youtube_token_kamishibai.json`。
Issue #38。

| 日時 | 版 | 動画ID | 状態 | 内容 |
|---|---|---|---|---|
| 2026-09-13 | v1 | （未アップロード） | — | 18:24（終了カード込み）。レンダ後レビューで S1 時計 4:12、S7 の写真の人種対比、S9 の海辺の女性たち、「二組」の誤読（ニクミ）が見つかり v2 に吸収。 |
| 2026-09-13 | v2 | SkhboCuCiJo | **非公開（試写用）** | 18:24（終了カード込み）。v1 のレビュー反映（二組→フタクミ、S1 時計 3:33、S1/S3/S6/S7/S9 の写真差し替え・前出し）。サムネ **A（暫定。ユーザー選択後に thumbnails().set で差し替え）**、字幕 ja、概要欄 description-v2.txt（章 10、v2 timeline）。 |

- 概要欄: `description-v1.txt`（`__CHAPTERS__` はレンダ後に `fill_chapters.py` 相当の手順で
  timeline.json から章時刻を埋めて `description-v2.txt` に書き出す）。タグ: `tags.txt`。
- サムネは `thumb-A.png` / `thumb-B.png` / `thumb-C.png`（1280×720、3案）。
  生成・合成スクリプトは `make_thumbs.py`。背景の生成元は `thumb-bg/orig/bg-{1,2,3}-raw.png`
  （Codex 生成、`thumb-bg/bg-{1,2,3}.png` が合成に使った作業用コピー）。
  採用案・確定後の下帯文言はユーザー選択後にここへ追記する。
- レンダ完了後、`--end-card` を付けて終了カードを含めること（前作からの申し送り）。
