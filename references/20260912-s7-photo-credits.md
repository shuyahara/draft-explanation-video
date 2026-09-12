# シーン7「恋は、いつ始まるのか」貼り写真クレジット（2026-09-12）

Issue #34（まとも男性ずんだもん版）新設シーン7用。友人期間を経て恋人になる人が3人に2人、という話に使う貼り写真。
保存先: `C:\Users\shuya\Projects\assets-kamishibai\photos\candidates-matome\stock\`

| ファイル名 | 内容 | 出典サイト | 撮影者 | ページURL | ライセンス | CREDIT辞書用文字列 |
|---|---|---|---|---|---|---|
| `s15_friends_laughing_a.jpg` | カフェのテーブルを囲む男女4人（女2・男2）がスマホで自撮りをしながら笑っている実写。ピザとコーヒーカップが手前に写る。 | Pexels | Vitaly Gariev | https://www.pexels.com/photo/friends-enjoying-coffee-and-pizza-together-36729772/ | commercial-ok | `Photo: Vitaly Gariev / Pexels` |
| `s15_friends_laughing_b.jpg` | 屋外カフェのテーブルで男女3人（男・女・男）がテイクアウトコーヒーを手に談笑している実写。 | Pexels | William Fortunato | https://www.pexels.com/photo/smiling-young-diverse-teenagers-drinking-coffee-and-chatting-in-street-cafe-6140394/ | commercial-ok | `Photo: William Fortunato / Pexels` |
| `s15_friends_walking_a.jpg` | 男女二人が横並びで屋外の遊歩道を歩いている実写（手はつながず、やや距離あり）。背景に "FRIENDS OF QUEENSBRIDGE PARK" の看板。 | Pexels | Liliana Drew | https://www.pexels.com/photo/a-man-and-woman-walking-together-8497661/ | commercial-ok | `Photo: Liliana Drew / Pexels` |
| `s15_friends_walking_b.jpg` | 男女二人が横並びで街の歩道を歩いている実写（手はつながず、それぞれ手荷物を持つ）。カジュアル寄りのオフィスカジュアル姿。 | Pexels | Felicity Tai | https://www.pexels.com/photo/man-and-woman-walking-on-sidewalk-7963826/ | commercial-ok | `Photo: Felicity Tai / Pexels` |
| `s15_couple_hands_a.jpg` | 手をつなぐ二人の手元のクローズアップ実写（顔は写らない）。 | Pexels | Nicole Lima | https://www.pexels.com/photo/close-up-photo-of-a-couple-s-hands-5915321/ | commercial-ok | `Photo: Nicole Lima / Pexels` |
| `s15_couple_hands_b.jpg` | 手をつなぐ二人の手元のクローズアップ実写（顔は写らない、屋外の草地背景）。 | Pexels | Gihan Bandara | https://www.pexels.com/photo/interracial-couple-holding-hands-outdoors-in-sri-lanka-37335091/ | commercial-ok | `Photo: Gihan Bandara / Pexels` |

## 検索・選定メモ

- 検索は `tools/stock_search.py`（script-to-video リポジトリ側）を使用。クエリ:
  - `friends group laughing outdoor cafe young adults`
  - `man and woman walking together outdoors side by side casual friends`
  - `man and woman colleagues talking walking outdoors casual not couple`（`_b` 探索用）
  - `couple holding hands closeup romantic`
- いずれも Pexels の候補を採用（Pixabay 候補は解像度・内容ともに Pexels 候補に劣ったため不採用）。
- `friends_walking` は「カップルに見えない」ことを優先し、手をつながず・距離のある構図を選定。候補の中には "couple" タグが付いた老年女性二人の白黒写真もあったが、男女ペアでなく用途に合わないため除外。
- 全ファイル、Pexels の原寸URL（`https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg`、クエリパラメータなし）から取得。幅はすべて 3800px 以上（目視確認済み、詳細は下表）。
- 保存後、全6枚を目視確認済み（友人グループに見えるか／カップルに見えるか）。差し替えは発生せず。

## 実測ピクセルサイズ

| ファイル | 幅×高さ |
|---|---|
| s15_friends_laughing_a.jpg | 3800×2138 |
| s15_friends_laughing_b.jpg | 5185×3457 |
| s15_friends_walking_a.jpg | 6000×4000 |
| s15_friends_walking_b.jpg | 6000×4000 |
| s15_couple_hands_a.jpg | 5184×3456 |
| s15_couple_hands_b.jpg | 6000×4000 |
