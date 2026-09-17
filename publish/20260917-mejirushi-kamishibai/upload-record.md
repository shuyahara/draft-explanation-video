# アップロード記録: めじるしアクセサリーはなぜ流行ったのか ― 6年前からあった商品が今年売り切れた理由（紙芝居版）

チャンネル: ずんだ人文学。トークン `script-to-video/secrets/youtube_token_kamishibai.json`。
Issue #40。

| 日時 | 版 | 動画ID | 状態 | 内容 |
|---|---|---|---|---|
| 2026-09-17 | v1 | VwSNZYYcDG0 | **非公開（試写用）** | 12:01（終了カード込み）。台本 v3（8 シーン・3,791 字）。レビュー 6 種＋間＋ビート適合表を反映。サムネ **A（暫定。ユーザー選択後に thumbnails.set で差し替え）**、字幕 ja、概要欄 description-v2.txt（章 8、v1 timeline）。 |
| | | | | |

- 概要欄: `description-v1.txt`（`__CHAPTERS__` はレンダ後に `fill_chapters.py` で
  timeline.json から章時刻を埋めて `description-v2.txt` に書き出す）。タグ: `tags.txt`。
- サムネは `thumb-A.png` / `thumb-B.png` / `thumb-C.png`（1280×720、3案）。
  生成・合成スクリプトは `make_thumbs_def.py`。背景の生成元は `thumb-bg/orig/bg-{A,B,C}-raw.png`
  （Codex 生成、`thumb-bg/bg-{A,B,C}.png` が合成に使った作業用コピー）。
  採用案・確定後の下帯文言はユーザー選択後にここへ追記する。
- レンダ完了後、`--end-card` を付けて終了カードを含めること。
