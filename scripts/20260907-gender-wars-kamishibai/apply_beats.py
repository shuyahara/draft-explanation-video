"""ずんだもん版・男女論: ビート（貼り写真 / 章カード / 黒板文字 / チョーク図解）と追加 readings を
YAML に貼り直す。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（冷笑版・ルッキズム版と同じ方式）。

  .venv\\Scripts\\python.exe scripts/20260907-gender-wars-kamishibai/apply_beats.py

前提: tools/kamishibai_md_to_yaml.py で YAML（narration 部）を生成済み。
貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-genderwars/scene_NN_beat{slot}.jpg`。

図解 8 箇所（型・layout の重複は各 2 回まで、隣接する図解ビートに同じ layout を置かない）:
  S3  sketch 3列2行（ブレイディの分析: 対象→操作→結果＋話題別の数字）
  S4  sketch 1行2列（同一研究内での比較。1倍 対 6.7倍）
  S5  sketch 3列2行（見出しを開く行動: 否定的な言葉・怒り・悲しみと、その結果）
  S6  sketch 2列2行（政治宗教と男女の話の対比）
  S8  narrative chain（怒りを書く→反応→また書きやすくなる）
  S9  narrative radiate（少数の発信者から三層に広がる）
  S10 sketch 2列2行（画面で見える日本と調査が見た日本。旧 S11）
  S11 narrative converge（今日の答えへの収束。旧 S12。旧 S10〔統計の章〕は v8 で削除）

黒板文字（board）の方針（docs/dialogue-guide.md §6）: 主題の定義・鍵になる用語・覚えてほしい要点・
論の区切りだけ。見出しは言葉そのもの（メタ語を使わない）。2 要素以上は ①②③。順序・因果・対比は図解へ。
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

YAML_PATH = Path(__file__).with_name("20260907-gender-wars-kamishibai.yaml")

# 出典表記（字幕帯右下）。候補 manifest（assets-kamishibai/photos/candidates-genderwars/manifest.md）
# の作者・ライセンスから採用分を転記する。TODO は素材確定後に差し替える。
CREDIT = {
    # Pexels License / Pixabay License（いずれも商用可・帰属は任意だが作者名を表示する）
    "bed1": "Photo: Jakub Zerdzicki / Pexels",
    "bed2": "Photo: cottonbro studio / Pexels",
    "cmt1": "Photo: thomas vanhaecht / Pexels",
    "cmt2": "Photo: Uriel Mont / Pexels",
    "cmt3": "Photo: William Fortunato / Pexels",
    "bill1": "Photo: Kaboompics.com / Pexels",
    "sink1": "Photo: Pixabay",
    "sink2": "Photo: Pixabay",
    "news1": "Photo: Pixabay",
    "news2": "Photo: Michael Burrows / Pexels",
    "news3": "Photo: weCare Media / Pexels",
    "f2f1": "Photo: Pavel Danilyuk / Pexels",
    "f2f2": "Photo: Pixabay",
    "type1": "Photo: RDNE Stock project / Pexels",
    "type2": "Photo: RDNE Stock project / Pexels",
    "type3": "Photo: RDNE Stock project / Pexels",
    "univ1": "Photo: Pixabay",
    "univ2": "Photo: Pixabay",
    "univ3": "Photo: Paul Loh / Pexels",
    "hall1": "Photo: Pixabay",
    "paper1": "Photo: Mike van Schoonderwalt / Pexels",
    "paper2": "Photo: Suzy Hazelwood / Pexels",
    "paper3": "Photo: Pixabay",
    "srv1": "Photo: Pixabay",
    "srv2": "Photo: panumas nikhomkhai / Pexels",
    "phone1": "Photo: JESHOOTS / Pexels",
    "phone2": "Photo: Sound On / Pexels",
    "phone3": "Photo: Jakub Zerdzicki / Pexels",
    "elec1": "Photo: Edmond Dantes / Pexels",
    "ad1": "Photo: Tahir Osman / Pexels",
    "ad2": "Photo: Clarence Chan / Pexels",
    "form1": "Photo: Pixabay",
    "form2": "Photo: Kindel Media / Pexels",
    "form3": "Photo: Willfried Wende / Pexels",
    "ans1": "Photo: Pixabay",
    "ans2": "Photo: RDNE Stock project / Pexels",
    "mtg1": "Photo: Pixabay",
    "us1": "Photo: Pixabay",
    "us2": "Photo: dumitru B / Pexels",
    "apart1": "Photo: miniperde / Pexels",
    "apart2": "Photo: Georgy Druzhinin / Pexels",
    "bag1": "Photo: Julia Larson / Pexels",
    "bag2": "Photo: Ivan S / Pexels",
    "neon1": "Photo: Mak_ jp / Pexels",
    "crowd1": "Photo: Pixabay",
    "crowd2": "Photo: Pixabay",
    "crowd3": "Photo: Pixabay",
    "exam1": "Photo: Andy Barbour / Pexels",
    "exam2": "Photo: Andy Barbour / Pexels",
    "train1": "Photo: Pixabay",
    "train2": "Photo: Kassandre Pedro / Pexels",
    "coin1": "Photo: Breakingpic / Pexels",
    "coin2": "Photo: Pixabay",
    "close1": "Photo: Roberto Cervantes / Pexels",
}

# 採用元ファイル（candidates-genderwars/{キー}/{キー}-N.jpg）→ render-assets へ配置するときの対応。
SOURCE_FILE = {
    "bed1": "bedroom-phone-light/bedroom-phone-light-1.jpg",
    "bed2": "bedroom-phone-light/bedroom-phone-light-2.jpg",
    "cmt1": "comment-scroll/comment-scroll-1.jpg",
    "cmt2": "comment-scroll/comment-scroll-2.jpg",
    "cmt3": "comment-scroll/comment-scroll-3.jpg",
    "bill1": "restaurant-bill/restaurant-bill-1.jpg",
    "sink1": "kitchen-sink/kitchen-sink-1.jpg",
    "sink2": "kitchen-sink/kitchen-sink-2.jpg",
    "news1": "news-site/news-site-1.jpg",
    "news2": "news-site/news-site-2.jpg",
    "news3": "news-site/news-site-3.jpg",
    # 候補1（並んで歩くカップル）は「面と向かって話す」と合わないので候補3（向かい合って座る二人）に差し替え
    "f2f1": "face-to-face/face-to-face-3.jpg",
    "f2f2": "face-to-face/face-to-face-2.jpg",
    "type1": "typing-phone/typing-phone-1.jpg",
    "type2": "typing-phone/typing-phone-2.jpg",
    "type3": "typing-phone/typing-phone-3.jpg",
    "univ1": "university-building/university-building-1.jpg",
    "univ2": "university-building/university-building-2.jpg",
    "univ3": "university-building/university-building-3.jpg",
    "hall1": "lecture-hall/lecture-hall-1.jpg",
    # 見出しの判読性が低い順に paper1 → paper2 → paper3。見出しが主題になる S5 だけ読める方を使う
    "paper1": "newspaper-headlines/newspaper-headlines-3.jpg",
    "paper2": "newspaper-headlines/newspaper-headlines-2.jpg",
    "paper3": "newspaper-headlines/newspaper-headlines-1.jpg",
    "srv1": "server-room/server-room-1.jpg",
    "srv2": "server-room/server-room-2.jpg",
    "phone1": "phone-viewing/phone-viewing-1.jpg",
    "phone2": "phone-viewing/phone-viewing-2.jpg",
    "phone3": "phone-viewing/phone-viewing-3.jpg",
    "elec1": "election-board/election-board-1.jpg",
    # billboard-1 は広告スクリーンの顔が大きいので不採用。billboard-3 は neon-ads-1 とほぼ同じ画なので不採用
    "ad1": "billboard/billboard-2.jpg",
    "ad2": "neon-ads/neon-ads-3.jpg",
    "form1": "survey-forms/survey-forms-1.jpg",
    "form2": "survey-forms/survey-forms-2.jpg",
    "form3": "survey-forms/survey-forms-3.jpg",
    "ans1": "survey-answer/survey-answer-1.jpg",
    "ans2": "survey-answer/survey-answer-2.jpg",
    "mtg1": "meeting-room/meeting-room-1.jpg",
    "us1": "us-street/us-street-1.jpg",
    "us2": "us-street/us-street-2.jpg",
    "apart1": "distance-two-people/distance-two-people-1.jpg",
    "apart2": "distance-two-people/distance-two-people-2.jpg",
    "bag1": "punching-bag/punching-bag-1.jpg",
    "bag2": "punching-bag/punching-bag-2.jpg",
    "neon1": "neon-ads/neon-ads-2.jpg",
    "crowd1": "crowd-distant/crowd-distant-1.jpg",
    "crowd2": "crowd-distant/crowd-distant-2.jpg",
    "crowd3": "crowd-distant/crowd-distant-3.jpg",
    "exam1": "exam-desk/exam-desk-1.jpg",
    "exam2": "exam-desk/exam-desk-2.jpg",
    "train1": "train-platform/train-platform-1.jpg",
    "train2": "train-platform/train-platform-2.jpg",
    # 候補2は「SALARY」のスクラブル文字が読めるので不採用。差の大きさが見える候補3を決め文に使う
    "coin1": "coins-wages/coins-wages-3.jpg",
    "coin2": "coins-wages/coins-wages-1.jpg",
    "close1": "phone-face-down/phone-face-down-1.jpg",
}

# 台本「発音・ポーズメモ」に書かれた読み。preflight の突合で追加・削除する。
GLOBAL_READINGS = [
    ("炎上", "エンジョウ"),
    ("拡散", "カクサン"),
    ("瀬地山角", "セチヤマカク"),
    ("主任", "シュニン"),
    ("係長", "カカリチョウ"),
    ("妥協", "ダキョウ"),
    ("賃金", "チンギン"),
    ("性交等", "セイコウトウ"),
    ("浜屋敏", "ハマヤサトシ"),
    ("田中辰雄", "タナカタツオ"),
    ("山口真一", "ヤマグチシンイチ"),
    ("中高年", "チュウコウネン"),
    ("痴漢", "チカン"),
    ("合格率", "ゴウカクリツ"),
    ("役職", "ヤクショク"),
    ("6.7倍", "ロクテンナナバイ"),
    ("14人に1人", "ジュウヨニンニヒトリ"),
    ("SNS", "エスエヌエス"),
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 間レビュー（references/20260907-...-pause-review.md）の指摘のうち、既定値（話者交代 0.45・
# 文境界 0.35）から動かす箇所。セグメント本文の一部で照合する。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    5: [("はっきりした関連が出なかったのよ", 0.7)],
    10: [("結果は逆だったのよ", 0.8)],
    11: [("問題まで消えるわけじゃないの", 0.7), ("関心まで失わないでほしいの", 0.8)],
}
# ナレーション版（元台本）の readings も、表記が本文に含まれるシーンへ転記する。
_V5 = Path("C:/Users/shuya/Projects/draft-explanation-video/scripts/20260824-net-gender-wars/20260824-net-gender-wars.yaml")
if _V5.exists():
    for _sc in yaml.safe_load(_V5.read_text(encoding="utf-8")).get("scenes", []):
        for _r in _sc.get("readings") or []:
            if (_r["surface"], _r["reading"]) not in GLOBAL_READINGS:
                GLOBAL_READINGS.append((_r["surface"], _r["reading"]))


def img(anchor, slot, credit_key, why, telop=None):
    return ("image", anchor, slot, credit_key, why, telop)


def board(anchor, why, telop=None):
    return ("board", anchor, None, None, why, telop)


def chapter():
    return ("chapter", None, None, None, "【章の入口】黒板に問いを書いて本題へ", None)


def diagram(anchor, why, spec):
    """チョーク図解。spec 内の `at` は文字列アンカーで書き、実行時にキュー番号へ解決する。"""
    return ("diagram", anchor, None, None, why, spec)


def cell(id, text=None, icon=None, at=None, after=None, value=None):
    c = {"id": id, "at": at}
    if icon:
        c["icon"] = icon
    if value:
        c["value"] = value
    if text:
        c["text"] = text
    if after:
        c["after"] = after
    return c


def sketch(rows, arrows=None, caption=None, highlight=None):
    spec = {"type": "sketch", "rows": rows}
    if arrows:
        spec["arrows"] = [{"from": a, "to": b} for a, b in arrows]
    if highlight:
        spec["highlight"] = highlight
    if caption:
        spec["caption"] = caption
    return spec


def chart(chart_type, source, points, at, title=None, unit=None):
    spec = {"type": "chart", "chart": chart_type}
    if title:
        spec["title"] = title
    if unit:
        spec["unit"] = unit
    if source:
        spec["source"] = source
    spec["series"] = [{"color": "accent", "at": at, "points": points}]
    return spec


BEATS = {
    1: [
        img(None, 1, "bed1", "【冒頭】暗い部屋でスマホの光だけが手元を照らす（顔なし・静止画）"),
        img("激しい言葉でお互いを責め合ってた", 2, "cmt1", "【燃えている投稿】責め合いのコメント欄へ（文字は読めない）"),
        img("怒りのコメントが何百件も", 3, "cmt2", "【何百件】コメント欄の別カットに替えて件数の多さへ"),
        img("こういうの、前にも何回も見た", 4, "bed2", "【既視感】暗い部屋の別カットに戻して、前にも何回も見た、へ"),
        img("おごるか割り勘か", 5, "bill1", "【入り口】伝票と財布。日常のどこにでも入り口がある話へ"),
        img("僕、前から不思議だったのだ", 6, "phone1", "【疑問】スマホを見る手元に替えて、ずんだもんの問いへ"),
        img("いい疑問ね", 7, "phone2", "【受け】スマホの別カットに替えて「研究でかなり分かっている」へ"),
    ],
    2: [
        img(None, 1, "news2", "【問いの確認】ニュースサイトを見る手元。ずんだもんの疑問を確かめ直す（定義の板は直編集で台詞ごと削除）"),
        board("答えを急ぐより、三つに分けて",
              "【この動画で確かめること】三つの問いを黒板の文字で（番号付き）",
              telop="今日確かめる三つのこと\n① どんな言葉が広がるのか\n② なぜ男女の話は特に燃えるのか\n③ 燃えているのは誰か"),
        img("一つ目と二つ目で", 2, "crowd1", "【三つに分ける理由】人混みの遠景へ。誰が・見え方まで調べる理由"),
        img("燃え広がる仕組みだけ見ていると", 3, "crowd3", "【二つに割れて見える】人混みの別カットに替えて、数えると見え方が変わる、へ"),
        img("じゃあ、一つ目なのだ", 4, "phone3", "【次章へ】スマホの別カットで「怒った投稿ばかり広がる」の問いへ"),
    ],
    3: [
        chapter(),
        img(None, 1, "hall1", "【心理学の導入】無人の大講義室。クロケットの枠組みへ",
            telop="Crockett (2017) Nat Hum Behav"),
        board("怒りを書き込みやすくする仕組みが三つある",
              "【鍵になる整理】三つの仕組みを黒板の文字で（番号付き）",
              telop="怒りが書きやすくなる理由\n① 目にする回数が増える\n② 書く負担が減る\n③ 反応が大きく返る"),
        img("三つ目は、怒って書いたときに", 2, "cmt3", "【手応え】いいねや返信が並ぶ画面へ（文字は読めない）"),
        img("面と向かって「あなたは間違っている」", 3, "f2f1", "【対面】向かい合って話す二人（後ろ姿）。言いにくさの場面"),
        img("でも画面の向こうになら", 4, "type1", "【画面越し】スマホに文字を打つ指先。決め文まで保持"),
        img("今度は、数字で確かめた研究", 5, "univ1", "【実証研究へ】大学の建物。ブレイディの分析の導入",
            telop="Brady et al. (2017) PNAS"),
        diagram(
            "分かったのは、こういうことよ",
            "【分析: ブレイディ2017】対象→着目した言葉→結果の格子。話題別の数字は発話に同期して出す",
            sketch(
                [
                    [
                        cell("subj", text="投稿を分析", icon="forum", value="56万件", at="分かったのは、こういうことよ"),
                        cell("op", text="感情の言葉が一つ", icon="search", at="そういう言葉が多い投稿ほど"),
                        cell("res", text="拡散されやすい", icon="trending_up", value="＋約2割", at="だいたい二割くらいね"),
                    ],
                    [
                        cell("t1", text="銃規制", value="19%", at="銃規制では19パーセント"),
                        cell("t2", text="同性婚", value="17%", at="銃規制では19パーセント", after="同性婚では17パーセント"),
                        cell("t3", text="気候変動", value="24%", at="気候変動では24パーセントよ"),
                    ],
                ],
                arrows=[("subj", "op"), ("op", "res")],
                caption={"text": "話題が変わっても同じ傾向", "at": "気候変動では24パーセントよ"},
            ),
        ),
    ],
    4: [
        img(None, 1, "type2", "【転換】スマホに文字を打つ指先（別カット）。もっと広がる言葉の予告"),
        board("相手をひとまとめにして",
              "【鍵になる用語】相手を名指しする言葉の定義を黒板の文字で",
              telop="相手を名指しする言葉\n「あいつら」とひとまとめに呼ぶ"),
        img("ケンブリッジ大学とニューヨーク大学の共同研究が", 2, "univ2", "【研究】大学の建物（別カット）。ラスジェの共同研究へ",
            telop="Rathje et al. (2021) PNAS"),
        img("敵として見る相手を指す言葉が一つ入ると", 3, "cmt3", "【67％】コメント欄。名指しする言葉が入るとシェアが増える話へ"),
        img("ここは注意してね", 0, "phone1", "【注意】スマホを見る手元。二割は別の研究の数字、の注意へ（旧: 板）"),
        diagram(
            "この研究の中で、道徳や感情の言葉",
            "【比較: 同一研究内】道徳・感情の言葉を1倍としたときの、相手を名指しする言葉の効き目",
            sketch(
                [
                    [
                        cell("base", text="道徳・感情の言葉", icon="chat_bubble", value="1倍",
                             at="この研究の中で、道徳や感情の言葉"),
                        cell("out", text="相手を名指しする言葉", icon="campaign", value="6.7倍",
                             at="この研究の中で、道徳や感情の言葉", after="およそ6.7倍だったの"),
                    ],
                ],
                highlight={"ids": ["out"], "at": "同じ研究の中で比べた数字なのだ"},
                caption={"text": "同じ研究の中で比べた効き目", "at": "この研究の中で、道徳や感情の言葉"},
            ),
        ),
        img("自分の側をほめた投稿と比べても", 4, "cmt2", "【2倍】コメント欄へ。ほめる投稿と責める投稿の差"),
        img("拡散をいちばん強く押し上げるのは", 5, "apart1", "【決め文】背を向け合う二人（顔なし）。間 2.0 秒を保持"),
    ],
    5: [
        img(None, 1, "paper2", "【別の行動へ】新聞紙面。見出しを開くかどうかの話に切り替える"),
        img("あるニュースサイトが実際にやっていた", 2, "paper1", "【比べ方】紙面の別カットで、見出しを二通り用意する話へ（旧候補はカップの商品名が読めた）"),
        img("その記録を、ニューヨーク大学などの研究チーム", 3, "univ3", "【研究】大学の建物（別カット）。570万クリックの分析へ",
            telop="Robertson et al. (2023) NHB"),
        diagram(
            "「悪い」「つらい」といった否定的な言葉",
            "【言葉と結果】見出しを開く行動で、どの言葉に関連が出て、どれに出なかったかを 3 列 2 行で",
            sketch(
                [
                    [
                        cell("w1", text="否定的な言葉", icon="trending_down", at="「悪い」「つらい」といった否定的な言葉"),
                        cell("w2", text="怒りの言葉", icon="local_fire_department", at="それが、怒りの言葉には、はっきりした関連が出なかった"),
                        cell("w3", text="悲しみの言葉", icon="sentiment_dissatisfied", at="悲しさを感じる見出しの方ね"),
                    ],
                    [
                        cell("r1", value="+2.3%", text="クリック率", at="クリック率は2.3パーセントほど高かったの"),
                        cell("r2", value="関連なし", at="それが、怒りの言葉には、はっきりした関連が出なかった", after="はっきりした関連が出なかったのよ"),
                        cell("r3", value="関連あり", at="怒りを出した見出しより、そちらが開かれていたの"),
                    ],
                ],
                highlight={"ids": ["w3", "r3"], "at": "怒りを出した見出しより、そちらが開かれていたの"},
                caption={"text": "見出しを開く行動", "at": "「悪い」「つらい」といった否定的な言葉"},
            ),
        ),
        img("どっちも本当よ", 0, "cmt2", "【束ねる】コメント欄。怒りに限らず否定的な言葉に反応する、の整理"),
        img("ここまでは、私たちが自分で何を開くか", 0, "type3", "【区切り】スマホに文字を打つ指先。自分で何を開くか、の話の締め"),
        img("でも、SNSの画面にどの投稿が表示されるかは", 0, "news2", "【並べる側へ】タブレットでニュースを見る手元。表示する順番は SNS の側が決めている、の転換"),
        img("その並べ方で何が目立つのかを、調べた研究", 4, "srv1", "【並べる側】サーバー室の機械。監査研究の導入",
            telop="Milli et al. (2025) PNAS Nexus"),
        img("反応の多い順の画面には、怒りを表す投稿", 5, "srv2", "【結果】サーバー室の別カットで、反応順の画面に怒りが多い話へ"),
        img("反応の多い順に並べた結果として", 6, "phone2", "【訂正】スマホを見る手元へ。誰かが怒りを選んだのではない、の一言"),
        img("画面に上がってくるのは", 7, "phone3", "【決め文】スマホの別カットで保持。間 2.0 秒"),
        img("でも、めたん", 8, "crowd1", "【次章への問い】人混みの遠景（脚のみ）。政治・宗教でも同じ仕組みのはず、の問いへ"),
    ],
    6: [
        chapter(),
        img(None, 1, "elec1", "【距離を置ける話題】選挙ポスターの掲示板（遠景）。政治・宗教は距離を置ける"),
        diagram(
            "でも男女の話は、多くの人が",
            "【対比: 話題の近さ】左＝政治・宗教／右＝男女の話。同じ列に同じ役割を置く",
            sketch(
                [
                    [
                        cell("l1", text="政治・宗教の話", icon="how_to_vote", at="でも男女の話は、多くの人が"),
                        cell("r1", text="男女の話", icon="wc", at="でも男女の話は、多くの人が"),
                    ],
                    [
                        cell("l2", text="関係ないと言える", icon="logout", at="でも男女の話は、多くの人が"),
                        cell("r2", text="自分に関わる話", icon="groups", at="「僕は関係ないのだ」って、画面の外に逃げにくいのだ"),
                    ],
                ],
                highlight={"ids": ["r2"], "at": "「僕は関係ないのだ」って、画面の外に逃げにくいのだ"},
            ),
        ),
        img("ここで、さっきの「相手を名指しする言葉」", 2, "cmt3", "【接続】コメント欄へ。大きな主語の話につなぐ"),
        board("「男は」「女は」という大きな主語が出ると",
              "【覚えてほしい要点】大きな主語が生む二つの受け取られ方を黒板の文字で（番号付き）",
              telop="「男は」「女は」と言われると\n① 責められたと感じる人が出る\n② 代弁されたと感じる人も出る"),
        img("責められたと思った人は言い返して", 3, "cmt1", "【両方が同時に】コメント欄。言い返す人と応援する人が同時に出る"),
        img("それと、これは私の意見だけど", 0, "type1", "【推論】スマホに文字を打つ指先。不満から書かれる投稿には否定的な言葉が入りやすい、の推論"),
        img("そう、だから男女論は炎上しやすいのよ", 0, "cmt2", "【小結】コメント欄。二つの性質が重なる、の小結"),
        img("こういう炎上の形は、昔から", 4, "ad1", "【広告の炎上】街頭の大きな広告看板（文字は読めない）",
            telop="瀬地山角『炎上CMでよみとくジェンダー論』"),
        img("たとえば、男は仕事、女は家事", 5, "sink1", "【役割の描き方】台所。役割分担の描かれ方へ"),
        img("その分析では、同じ型の炎上が", 6, "ad2", "【型の反復】広告看板の別カットで、同じ型が繰り返される話へ"),
        img("ここまでの研究は政治の話題で調べたものが多いから", 0, "univ3", "【適用範囲の留保】大学の建物。政治の話題で調べた研究が多い、の一言（旧: 板）"),
        board("でも、仕組みはつながっているの",
              "【この動画の答え】男女の話が燃えやすい理由を二つに束ねる（主軸の決め文）",
              telop="男女の話が燃えやすい理由\n① 燃えやすい言葉が入りやすい\n② 全員が当事者になる"),
        img("炎上する時の言い争いを実際に投稿してるのは", 7, "phone1", "【次章へ】スマホを見る手元。書いている人への問いへ"),
    ],
    7: [
        chapter(),
        img(None, 1, "form1", "【日本の調査】アンケート用紙の束。6万人規模の調査の導入",
            telop="山口真一・田中辰雄『ネット炎上の研究』"),
        img("アンケートだけじゃなくて、ツイッターの分析", 2, "cmt1", "【手法】コメント欄へ。ツイッターの分析も合わせている話"),
        img("調べたのは、50回以上リツイート", 3, "cmt2", "【対象】コメント欄の別カットで、対象にした炎上の条件へ"),
        board("一年以内に書き込んだ人は",
              "【覚えてほしい要点】炎上に書き込む人の割合を黒板の文字で（番号付き）",
              telop="炎上に書き込んだ人\n① この一年で 0.5％\n② 一度でも 1.1％"),
        img("つまり、あれだけ荒れて見えても", 4, "crowd1", "【決め文】人混みの遠景で保持。適用範囲のテロップを重ねる。間 2.5 秒",
            telop="0.5％は炎上全体が対象／男女論だけを数えた数字ではない"),
        img("その0.5パーセントって、よっぽど暇な人", 5, "type3", "【予想】スマホを見る手元。ずんだもんの決めつけと言い直し"),
        board("書き込む動機は、6割から7割が正義感",
              "【覚えてほしい要点】書き込む人の動機と属性を黒板の文字で（番号付き）",
              telop="書き込んでいる人\n① 6〜7割は正義感\n② 男性が多い\n③ 役職が上の人が多い"),
        img("え、会社で偉い人なのだ", 6, "mtg1", "【意外な属性】無人のオフィスの会議机へ"),
        img("でも、まだ腑に落ちないのだ", 8, "apart2", "【次章への問い】距離を置いて立つ二人（顔なし）。なぜ引かないのか、へ"),
    ],
    8: [
        img(None, 1, "hall1", "【心理の章へ】無人の大講義室。スキトカの研究の導入",
            telop="Skitka ほか（イリノイ大学シカゴ校）"),
        board("これは好みの違いじゃない",
              "【鍵になる用語】善悪の問題だと感じている意見、を黒板の文字で",
              telop="善悪の問題だと思うと\n譲ることが「悪に負ける」になる"),
        img("好き嫌いじゃなくて、善悪の問題", 2, "apart1", "【妥協しにくさ】背を向け合う二人（顔なし）。譲れない状態の画"),
        img("でも善悪の問題だと思っていると", 3, "f2f2", "【譲れない】向かい合って話す二人（後ろ姿）。譲ることが悪に負けることになる"),
        img("そして、やめにくさを強めるものが", 4, "form3", "【もう一つの力】研究資料の束。イェールの研究へ（大学の建物は S3 と同じ写真になり別大学の誤認を招くため差し替え）",
            telop="Brady et al. (2021) Sci. Adv."),
        diagram(
            "怒りを込めた投稿にたくさん反応がつくと",
            "【循環: 社会的強化学習】怒りを書く→反応がつく→その後も書きやすくなる",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "write", "text": "怒りを込めて書く", "icon": "edit", "at": "怒りを込めた投稿にたくさん反応がつくと"},
                    {"id": "react", "text": "反応がつく", "icon": "thumb_up", "at": "その後も怒りを込めた投稿を書きやすくなっていたわ"},
                    {"id": "again", "text": "また書きやすい", "icon": "replay", "at": "反応が返ると、次も強いことを書きやすくなるのだ"},
                ],
                "caption": {"text": "反応が次の投稿を後押しする", "at": "同じ研究チームが別におこなった実験でも"},
            },
        ),
        img("それと、怒りは吐き出せばすっきりする", 5, "bag1", "【通説】無人のジムのサンドバッグ。発散すればすっきりする、という通説",
            telop="Bushman (2002) PSPB"),
        img("サンドバッグをたたいて怒りを発散させても", 6, "bag2", "【反証】サンドバッグの別カット。決め文まで保持。間 2.0 秒"),
        img("じゃあ、あの人たちは目立ちたいだけなのだ", 7, "phone2", "【早合点】スマホを見る手元。目立ちたいだけ、という決めつけへ"),
        img("そこは、決めつけないでおきましょう", 8, "apart2", "【限定】距離を置く二人の別カット。内心は測っていない、の留保"),
        img("……でも、書いてるのは、たった0.5パーセント", 9, "phone1", "【次章への仮説】スマホの別カット。少数がなぜ大勢に見えるか、へ"),
    ],
    9: [
        chapter(),
        img(None, 1, "cmt2", "【二つをつなぐ】コメント欄。広がりやすい投稿と、書く人の少なさ"),
        img("広告で収入を得るサービスでは", 2, "neon1", "【仕組み】ネオンの広告が並ぶ夜の街。見てもらう時間が売り上げになる"),
        img("少ない人の声が、繰り返し目立つ場所に", 3, "crowd1", "【押し上げ】人混みの遠景（脚のみ）。少ない声が繰り返し目立つ場所に出てくる"),
        img("ある女性ジャーナリストに向けられた中傷", 4, "cmt1", "【日本の実例】コメント欄の別カット。2800件の返信を分類した研究へ",
            telop="Tonami et al. (2022) F1000Res."),
        diagram(
            "攻撃の中心にいたのは、ごく少数の",
            "【三層: 拡散の広がり】中心の少数から、引用・まね、内容に関係ない攻撃へ広がる",
            {
                "type": "narrative",
                "layout": "radiate",
                "center": {"icon": "campaign", "text": "少数の発信者", "at": "攻撃の中心にいたのは、ごく少数の"},
                "items": [
                    {"id": "quote", "text": "引用して広める", "at": "その投稿を引用したり、まねて書いたりする人が続くの"},
                    {"id": "mimic", "text": "まねて書く人", "at": "その投稿を引用したり、まねて書いたりする人が続くの", "after": "まねて書いたり"},
                    {"id": "pile", "text": "攻撃に加わる人", "at": "最後に、内容に関係なく攻撃に加わる人が増えていったわ"},
                ],
                "turn": {"at": "研究チームは、そういう三つの層が重なる形を見つけたのよ"},
            },
        ),
        img("少数の声でも、実際の人数よりずっと大きく", 9, "crowd3", "【決め文】人混みの遠景で保持。間 2.0 秒"),
    ],
    10: [
        chapter(),
        img(None, 1, "form2", "【分断の調査】アンケート用紙の束（別カット）。田中・浜屋の調査へ",
            telop="田中辰雄・浜屋敏『ネットは社会を分断しない』"),
        img("そのうち5万人から回答を集めて", 2, "form3", "【規模】用紙の別カット。10万人規模・5万人回答の内訳へ"),
        img("同じ意見の人ばかり見て", 3, "cmt2", "【通説】コメント欄。同じ意見ばかり見て過激になる、という通説"),
        diagram(
            "ネットを使っている人ほど",
            "【対比: 画面の日本と調査の日本】左＝画面で見える日本／右＝調査が見た日本",
            sketch(
                [
                    [
                        cell("l1", text="画面で見える日本", icon="smartphone", at="ネットを使っている人ほど"),
                        cell("r1", text="調査が見た日本", icon="insights", at="ネットを使っている人ほど"),
                    ],
                    [
                        cell("l2", text="二つに割れている", icon="call_split", at="ネットを使っている人ほど"),
                        cell("r2", text="反対意見にも触れる", icon="handshake", at="そして、反対の意見に触れていた人ほど"),
                    ],
                ],
                highlight={"ids": ["r2"], "at": "そして、反対の意見に触れていた人ほど"},  # 中高年の層を金色で強調すると「中高年が悪い」と読めるので、強調は穏健化の方だけ
            ),
        ),
        img("この結果は、総務省の情報通信白書", 4, "news1", "【裏付け】資料を読む手元。白書でも紹介されている話へ"),
        img("ここまでの話とつなげると", 5, "crowd1", "【整理】人混みの遠景（脚のみ）。全体と目立つ場所の違いへ"),
        img("そして、その「目立つ場所」を作っている仕掛け", 6, "cmt3", "【呼び名へ】コメント欄の別カット。相手をひとまとめに呼ぶ言葉へ"),
        board("なんとかフェミとか、弱者男性とか",
              "【鍵になる用語】ネットの呼び名の位置づけを黒板の文字で",
              telop="ネットの呼び名\n＝ 相手側をひとまとめに指す言葉"),
        img("そして思い出してほしいのだけれど", 7, "type2", "【接続】スマホに文字を打つ指先。相手を名指しする言葉の効果へ戻す"),
        img("そういう呼び名が広まると", 8, "crowd3", "【決め文】人混みの遠景で保持。間 2.5 秒"),
    ],
    11: [
        img(None, 1, "bed1", "【回帰】冒頭と同じ暗い部屋のスマホ。最初の疑問へ戻る"),
        diagram(
            "まず、怒りや否定的な言葉と",
            "【収束: 最初の疑問への答え】ずんだもんのまとめに同期して 1 項目ずつ出し、「だから燃えやすい」へ収束させる",
            {
                "type": "narrative",
                "layout": "converge",
                "items": [
                    {"id": "word", "text": "広がる言葉", "at": "まず、怒りや否定的な言葉と"},
                    {"id": "order", "text": "反応順の画面", "at": "しかも、反応の多い順に並ぶ画面が"},
                    {"id": "party", "text": "全員が当事者", "at": "そして男女の話は"},
                    {"id": "enemy", "text": "敵の名指しと不満", "at": "「男は」「女は」という言い方が"},
                ],
                "result": {"text": "だから男女の話は燃えやすい", "at": "だから、他の話題より燃えやすいのだ"},
            },
        ),
        img("よくまとまったわね", 3, "phone1", "【受け止め】スマホの別カット。最初の疑問への答えを受け止める"),
        img("反応がつくと書き続けやすくなるから", 2, "type2", "【補足】スマホを見る手元。反応が書き手を後押しする話"),
        img("あなたが見たのは、男の人と女の人が", 4, "cmt1", "【冒頭の回収】コメント欄。実際に書いていたのはごく一部だった"),
        board("世の中全体が憎み合っているかどうかは",
              "【論の着地】この動画で言えることの範囲を黒板の文字で",
              telop="画面の激しさだけでは\n世の中全体は分からない"),
        img("賃金の差や家事の時間の偏りのように", 5, "crowd3", "【残る問題】人混みの遠景。画面の外にいる人たちの問題は男女どちらの側にも残る",
            telop="画面の外の問題は、男女どちらの側にも残る"),
        img("だから、画面の激しさに慣れて", 6, "sink2", "【関心を失わない】洗い物の手元。現実の問題の画へ"),
        img("じゃあ、また今日も炎上している投稿を見たら", 7, "bed2", "【回帰】暗い部屋の別カット。冒頭の夜の場面へ戻る"),
        img("男女の論争が燃えやすいのは", 8, "close1", "【最後の一枚】暗い部屋でスマホを伏せて置く手。決め文（仕組みで締める）をアウトロまで保持。間 2.5 秒"),
    ],
}


def cues_of(scene) -> list[str]:
    """字幕キューの本文列。分割規則は script-to-video の `text_cues.split_into_sentences` と同じものを使う。"""
    sys.path.insert(0, "C:/Users/shuya/Projects/script-to-video/src")
    from script_to_video.text_cues import split_into_sentences

    out = []
    for seg in scene["narration"]:
        out.extend(p for p in split_into_sentences(seg["text"]) if p.strip())
    return out


MISSING: list[str] = []


def resolve(cues: list[str], anchor: str | None, scene_id: int) -> int:
    if anchor is None:
        return 1
    for i, c in enumerate(cues, 1):
        if anchor in c:
            return i
    MISSING.append(f"scene {scene_id}: anchor not found: {anchor!r}")
    return 10**6


def resolve_ats(spec, cues: list[str], scene_id: int):
    def walk(node):
        if isinstance(node, dict):
            return {k: (resolve(cues, v, scene_id) if k == "at" and isinstance(v, str) else walk(v)) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        return copy.deepcopy(node)

    return walk(spec)


def main() -> None:
    doc = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    total = 0
    for scene in doc["scenes"]:
        sid = scene["id"]
        cues = cues_of(scene)
        beats = []
        last_from = 0
        img_i = 0
        for kind, anchor, slot, ckey, why, telop in BEATS[sid]:
            if kind == "chapter":
                beats.append({"type": "chapter", "cut_reason": why})
                continue
            frm = resolve(cues, anchor, sid)
            if frm >= 10**6:
                continue
            if frm <= last_from:
                MISSING.append(f"scene {sid}: from must increase ({anchor!r} -> {frm} <= {last_from})")
                continue
            last_from = frm
            b = {"type": kind, "cut_reason": why, "from": frm}
            if kind == "image":
                img_i += 1
                b["slot"] = img_i  # 画像ビートの通し番号（img() の slot 引数は無視する。板の抜き差しで番号がずれないように）
                b["credit"] = CREDIT[ckey]
            if kind == "diagram":
                b["diagram"] = resolve_ats(telop, cues, sid)
            elif telop:
                b["telop"] = telop
            beats.append(b)
        scene["beats"] = beats
        total += len(beats)
        for frag, sec in PAUSE_OVERRIDES.get(sid, []):
            hit = [seg for seg in scene["narration"] if frag in seg["text"]]
            if len(hit) != 1:
                MISSING.append(f"scene {sid}: pause override matched {len(hit)} segments: {frag!r}")
                continue
            hit[0]["pause_after"] = sec
        text = "".join(seg["text"] for seg in scene["narration"])
        extra = [(s, r) for s, r in EXTRA_READINGS.get(sid, []) + GLOBAL_READINGS if s in text]
        if extra:
            rs = scene.get("readings") or []
            have = {r["surface"] for r in rs}
            rs.extend({"surface": s, "reading": r} for s, r in extra if s not in have)
            scene["readings"] = rs
        print(f"scene {sid:>2}: {len(cues):>2} cues, {len(beats)} beats  from={[b.get('from') for b in beats if 'from' in b]}")
    if MISSING:
        raise SystemExit("\n".join(MISSING))
    with YAML_PATH.open("w", encoding="utf-8", newline="\n") as f:
        yaml.dump(doc, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"beats written: {total}")


if __name__ == "__main__":
    main()
