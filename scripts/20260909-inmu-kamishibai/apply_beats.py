"""めたん×ずんだもん版・淫夢: ビート（貼り写真 / 章カード / 黒板文字 / チョーク図解）と追加
readings・pause_after を YAML に貼り直す。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（男女論版・ルッキズム版と同じ方式）。

  .venv\\Scripts\\python.exe scripts/20260909-inmu-kamishibai/apply_beats.py

前提: tools/kamishibai_md_to_yaml.py で YAML（narration 部）を生成済み。
貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-inmu/scene_NN_beat{slot}.*`。

図解 5 箇所（型・layout の重複は各 2 回まで、隣接する図解ビートに同じ layout を置かない）。
2026-09-09 絵コンテ点検（オーケストレーター目視）で各図解の保持が長すぎた（S3 74秒・S5 52秒・
S6 39秒）ため、前振り部分を image ビートへ譲って図解の保持を短縮した:
  S2 sketch 2行3列（年表: 2001発売→2007転載→2008音MAD→2010例のアレ→2014週間タグ1位。
     2020年代TikTokは6セル目に詰め込まず、直後の実写ストック写真に譲る）
  S3 sketch 2列3行を2段階（台本 v5、2026-09-09 ユーザー提案）: 図解2aで Shifman 2012 の
     抽象6特徴を、めたんの列挙の各語に合わせて1セルずつ出す（台詞の頭から。前振りimageビートは
     置かない）。図解2bで同じ2列3行・同じ位置に淫夢への当てはめ5項目を1セルずつ出し、
     ⑥は？のまま「はっきり当てはまるわ」でハイライト。以降は papercraft の image ビートへ
  S5 narrative converge（良性侵犯理論: 規則違反＋安全の両立→笑い。前振り「人はどういうときに
     笑うのか」は friends_laugh の image ビートへ）
  S6 narrative chain（N次創作の循環。chain は輪を表現できないため caption「また最初に戻る」で示す。
     素材の切り出し・N次創作の紹介は typing_hands の image ビートへ譲り、図解は
     「部品を組み合わせた動画が上がり」から決め文までに短縮）
  S7 sketch 3行2列（ヘリントン対比: 見出し行＋選択の有無＋結果の3行2列、選択の行から結果の行へ縦矢印）

黒板文字（board）の方針（docs/dialogue-guide.md §6）: 主題の定義・鍵になる用語・覚えてほしい要点・
論の区切りだけ。見出しは言葉そのもの（メタ語を使わない）。2要素以上は①②③。順序・因果・対比は図解へ。
S4 は台本指定どおり定義1行のみ。S8 は見出し込み4行上限に収めるため①②を1行、③④を1行に結合。

スロット名の対応（台本「画面」欄の呼び名 → 素材ワーカー manifest の実ファイル名）:
  ill_comment_top      -> illust/ill_comment_feed.png
  ill_old_dvd          -> illust/ill_dvd_shelf.png
  ill_classroom        -> illust/ill_classroom_laugh.png
  ill_circle_outside   -> illust/ill_circle_outsider.png
  ill_headphones_night -> illust/ill_headphones_laugh.png
  ill_shape_wall       -> illust/ill_shape_wall.png（一致）
  ill_nico_comments    -> illust/ill_niconico_comments.png
  ill_many_hands       -> illust/ill_typing_hands.png
  ill_laugh_circle_back -> illust/ill_circle_laugh_turned.png
  ill_event_back       -> illust/ill_fan_event_back.png
  ill_alone_phone_back -> illust/ill_dark_room_phone.png
  S3「机の上で紙の切れ端を組み合わせる手元（ストック）」は candidates 収集時に候補が
  抜けていたため、2026-09-09 に tools/stock_search.py で追加取得（stock-candidates.md 追記済み）。

2026-09-09 絵コンテ点検で追加取得したストック（stock-candidates.md 追記済み。すべて
tools/stock_search.py で検索）:
  selfie_video -> stock/scene3_vlogger_man_1.jpg（自宅でスマホ三脚に向かって動画を撮る男性。v1は女性の自撮りで映像レビュー⑦の指摘を受けv2で男性に差し替え）
  app_feed     -> stock/scene2_app_feed_1.jpg（動画配信アプリのサムネイル一覧をスクロールする手元）
  friends_laugh -> stock/scene5_friends_laugh_1.jpg（友人同士で笑っている数人）
  protest      -> stock/scene7_protest_1.jpg（抗議のプラカードを持つ人々。特定団体ロゴなし）
  whisper は scene3_whisper_1.jpg（暗い書斎でノワール調、場面に不一致）から
  scene3_whisper_2.jpg（明るい部屋で笑いながら耳打ち）を経て、v2で scene4_whisper_clear_1.jpg
  （手のひらで口元から耳元までを完全に覆う構図。v1のscene3_whisper_2.jpgは頬にキスして
  いるように見えるとの指摘）へ差し替え。
  old_dvd_photo -> stock/scene1_dvd_shelf_stock.jpg（v2追加。S1「二十五年前」用。
  illust/ill_dvd_shelf.png は図書館に見えるためS1のみストック写真に差し替え。S2冒頭の
  つなぎカットは引き続きill_dvd_shelf.pngを使用）
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

YAML_PATH = Path(__file__).with_name("20260909-inmu-kamishibai.yaml")

# 出典表記（字幕帯右下）。candidates-inmu/{stock,illust}-candidates.md の作者・ライセンスから転記。
CREDIT = {
    "famous_face": "© COAT Corporation（2001）より。引用",
    "watch1": "Photo: Pixabay",
    "comment_top": "Illustration: AI generated",
    "old_dvd": "Illustration: AI generated",
    "old_dvd_photo": "Photo: Pixabay / Pexels",
    "tiktok": "Photo: Artem Podrez / Pexels",
    "classroom": "Illustration: AI generated",
    "circle_outsider": "Illustration: AI generated",
    "whisper": "Photo: RDNE Stock project / Pexels",
    "headphones": "Illustration: AI generated",
    "shape_wall": "Illustration: AI generated",
    "papercraft": "Photo: Ksenia Chernaya / Pexels",
    "nico_comments": "Illustration: AI generated",
    "typing_hands": "Illustration: AI generated",
    "circle_laugh_turned": "Illustration: AI generated",
    "fan_event_back": "Illustration: AI generated",
    "dark_room_phone": "Illustration: AI generated",
    "selfie_video": "Photo: Ron Lach / Pexels",
    "app_feed": "Photo: cottonbro studio / Pexels",
    "friends_laugh": "Photo: Antonius Ferret / Pexels",
    "protest": "Photo: Oriel Frankie Ashcroft / Pexels",
    "herrington_portrait": "Photo: ガジェット通信",
}

# 採用元ファイル（candidates-inmu/{相対パス}）→ render-assets へ配置するときの対応。
SOURCE_FILE = {
    "famous_face": "famous-face-eyebar-800.png",
    "watch1": "stock/scene1_watching_phone_2.jpg",
    "comment_top": "illust/ill_comment_feed.png",
    "old_dvd": "illust/ill_dvd_shelf.png",
    "old_dvd_photo": "stock/scene1_dvd_shelf_stock.jpg",
    "tiktok": "stock/scene2_tiktok_dance_1.jpg",
    "classroom": "illust/ill_classroom_laugh.png",
    "circle_outsider": "illust/ill_circle_outsider.png",
    "whisper": "stock/scene4_whisper_clear_1.jpg",
    "headphones": "illust/ill_headphones_laugh.png",
    "shape_wall": "illust/ill_shape_wall.png",
    "papercraft": "stock/scene3_papercraft_1.jpg",
    "nico_comments": "illust/ill_niconico_comments.png",
    "typing_hands": "illust/ill_typing_hands.png",
    "circle_laugh_turned": "illust/ill_circle_laugh_turned.png",
    "fan_event_back": "illust/ill_fan_event_back.png",
    "dark_room_phone": "illust/ill_dark_room_phone.png",
    "selfie_video": "stock/scene3_vlogger_man_1.jpg",
    "app_feed": "stock/scene2_app_feed_1.jpg",
    "friends_laugh": "stock/scene5_friends_laugh_1.jpg",
    "protest": "stock/scene7_protest_1.jpg",
    "herrington_portrait": "stock/herrington-portrait.jpg",
}

# 台本「発音・ポーズメモ」に書かれた読み。preflight の突合で追加・削除する。
GLOBAL_READINGS = [
    ("淫夢", "インム"),
    ("例のアレ", "レイノアレ"),
    ("音MAD", "オトマッド"),
    ("打田", "ウチダ"),
    ("良性侵犯", "リョウセイシンパン"),
    ("濱野", "ハマノ"),
    ("N次創作", "エヌジソウサク"),
    ("擬似同期", "ギジドウキ"),
    ("表に", "オモテニ"),
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {
    1: [("いちばん上に", "イチバンウエニ")],
}

# 間レビュー前の一次反映: 台本「発音・ポーズメモ」のうち（間 N）で明示済みでないもの
# （デフォルト値: 話速1.1で話者交代0.45・文境界0.35・章末1.2から動かす箇所）。
# セグメント本文の一部で照合する（pause_after はセグメント末尾に効くので、末尾の一文を指定する）。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [("笑いになるのだ", 0.9), ("合言葉として使われているのか", 1.2)],
    2: [("生き残ったのか", 0.8), ("切り貼りしやすい形って、どういう形なのだ", 0.7)],
    3: [
        ("そして笑える", 0.45),
        ("はっきり当てはまるわ", 0.45),
        ("理由にはならないわ", 0.7),
        ("何が嬉しいのだ", 1.2),
    ],
    4: [("合言葉になったのか", 0.8), ("対抗することだったの", 0.45)],
    5: [("1968年に示したの", 0.45), ("ニコニコ動画だったのだ", 1.2)],
    6: [("面白さではなく仕組みだった", 0.9), ("別にいるかもしれないということよ", 2.0)],
    7: [("実在するの", 0.9), ("別なのよ", 2.0)],
    8: [("重なったからなのだ", 0.45), ("今日の話はここまで", 2.5)],
}


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


BEATS = {
    1: [
        img(None, 1, "watch1", "【日常の入り口】料理動画を見る手元から始める"),
        img("やりますねぇ", 2, "comment_top", "【核心のコメント】ピン留めコメントと桁違いのいいね数を再現（文字は描かない）"),
        img("僕にはさっぱり分からなかったのだ", 3, "comment_top", "【間】同じ絵のまま、ずんだもんの困惑まで尺を分ける"),
        img("知っている人にだけ通じる合言葉", 4, "watch1", "【間】めたんの受けで手元カットに戻し尺を分ける"),
        img("25年くらい前に出た", 4, "old_dvd_photo", "【時代を示す】DVDケースが並ぶ棚のストック写真で『25年前』を視覚化（v1のill_dvd_shelfは図書館に見えたため差し替え）"),
        img("そんな古いものの台詞が", 5, "comment_top", "【問いへの折り返し】コメント欄に戻り、なぜ今も笑いになるのかへ"),
        img("作品の中身は説明しないわ", 6, "watch1", "【留保】手元カットに戻し、中身は説明しない旨と締めの受けを保持"),
    ],
    2: [
        chapter(),
        img(None, 1, "old_dvd", "【つなぎ】前シーンと同じ棚の絵で始め、歴史の説明へ入る"),
        img("2001年に発売された", 2, "famous_face", "【出典の明示】黒線入り静止画を出所テロップ付きで提示",
            telop="© COAT Corporation（2001）より。引用"),
        diagram(
            "あとから同じ制作会社の作品まで含めて",
            "【年表】2001→2014の5イベントを2列3行で振り返る。2020年代TikTokはこの図に詰め込まず、直後の実写で見せる",
            sketch(
                [
                    [
                        cell("y2001", text="2001 発売", icon="movie", at="あとから同じ制作会社の作品まで含めて"),
                        cell("y2007", text="2007 転載", icon="upload", at="ニコニコ動画にその映像が転載されたの", after="ニコニコ動画にその映像が転載されたの"),
                        cell("y2008", text="2008 音MAD", icon="music_note", at="音MADの素材にされ始めたわ", after="音MADの素材にされ始めたわ"),
                    ],
                    [
                        cell("y2010", text="2010 例のアレ", icon="folder", at="「例のアレ」というカテゴリができたの", after="「例のアレ」というカテゴリができたの"),
                        cell("y2014", text="2014 タグ1位", icon="trending_up", at="週間のタグ人気で一位になったこともあるわ"),
                        None,
                    ],
                ],
                arrows=[("y2001", "y2007"), ("y2007", "y2008"), ("y2008", "y2010"), ("y2010", "y2014")],
            ),
        ),
        img("TikTok のダンス", 2, "tiktok", "【現代への橋渡し】ダンス動画で今の使われ方を実写で見せる"),
        img("なぜこれだけが25年も生き残ったのか", 3, "app_feed", "【問いの再提示】動画アプリのサムネイル一覧をスクロールする手元に替え、なぜ生き残ったのかを問う（棚の絵の再掲は婉曲だったため差し替え）"),
        img("面白さだけでは、25年は続かないの", 4, "tiktok", "【決め文の保持】ダンス動画に戻し、決め文の間1.5秒まで保持"),
    ],
    3: [
        diagram(
            None,
            "【6特徴・抽象】Shifman(2012)の6特徴をsketch 2列3行で、めたんの列挙の各語に合わせて1セルずつ出す（図解2a）。前振りの写真は置かず台詞の頭から出す",
            sketch(
                [
                    [
                        cell("a1", text="①普通の人", at="普通の人が出ていて", after="普通の人が出ていて"),
                        cell("a2", text="②男らしさの欠如", at="男らしさがどこか欠けて見えて", after="男らしさがどこか欠けて見えて"),
                    ],
                    [
                        cell("a3", text="③単純", at="単純で", after="単純で"),
                        cell("a4", text="④繰り返し", at="繰り返しがあって", after="繰り返しがあって"),
                    ],
                    [
                        cell("a5", text="⑤奇妙", at="奇妙で", after="奇妙で"),
                        cell("a6", text="⑥笑える", at="そして笑える", after="そして笑える"),
                    ],
                ],
            ),
        ),
        diagram(
            "淫夢の素材に当てはめてみましょう",
            "【6特徴・淫夢への置き換え】図解2aと同じ2列3行・同じ位置に淫夢の要素を1セルずつ出す（図解2b）。⑥は？のまま保持し、『はっきり当てはまるわ』でf1〜f5をハイライト",
            sketch(
                [
                    [
                        cell("b1", text="①素人に近い出演者", at="素人に近い出演者", after="素人に近い出演者"),
                        cell("b2", text="②締まらない演技", at="締まらない演技", after="締まらない演技"),
                    ],
                    [
                        cell("b3", text="③短い言い回し", at="短い言い回し", after="短い言い回し"),
                        cell("b4", text="④繰り返せる場面", at="繰り返せる場面", after="繰り返せる場面"),
                    ],
                    [
                        cell("b5", text="⑤意味不明のやり取り", at="意味の分からないやり取り", after="意味の分からないやり取り"),
                        cell("b6", text="⑥？", at="素人に近い出演者"),
                    ],
                ],
                caption={"text": "淫夢に当てはめると", "at": "淫夢の素材に当てはめてみましょう"},
                highlight={"ids": ["b1", "b2", "b3", "b4", "b5"], "at": "はっきり当てはまるわ", "after": "はっきり当てはまるわ"},
            ),
        ),
        img("淫夢そのものを調べた研究も見るわ", 3, "papercraft", "【比喩の直接化】『切り刻んで遊ぶ』を机上の紙細工の手元で見せる。図解のあとに切り替え"),
        img("そういうこと", 4, "papercraft", "【間】同じ絵のまま、決め文の余韻まで尺を分ける（保持28秒を短縮するため分割）"),
    ],
    4: [
        chapter(),
        img(None, 1, "classroom", "【自分は分かる側】教室で一人だけ落書きに笑う生徒（記号のみ）",
            telop="社会的アイデンティティ理論"),
        img("イギリスのブリストル大学のタジフェル教授と", 2, "circle_outsider", "【出典の提示】輪の絵に替え、Tajfel & Turnerの提唱年を見せる"),
        img("その境目を作る道具の一つが言葉なの", 2, "circle_outsider", "【間】同じ絵のまま、境目を作る言葉の話へ尺を分ける（研究者肩書き追加で保持20.9秒を短縮するため分割）"),
        img("仲間かどうかの境目になるのだ", 3, "classroom", "【内と外の境目・再掲】教室の絵に戻り、境目の話を続ける",
            telop="Eble 1996: 大学生の俗語1万例以上"),
        img("淫夢の語録は、まさにこれね", 4, "circle_outsider", "【当てはめ】輪の絵に戻り、淫夢の語録への当てはめへ"),
        img("淫夢そのものを調べた研究を見ましょう", 5, "whisper", "【表に出したくないが広まってほしい】ひそひそ話をする二人",
            telop="打田 2024: 14人への聞き取り"),
        img("分かったのは、使う人たちは", 6, "whisper", "【間】同じ絵のまま、打田の調査結果の話へ尺を分ける"),
        img("表に出したくないけど", 7, "classroom", "【矛盾の受け止め】教室の絵に戻り、矛盾する気持ちの話へ"),
        board("語録は笑いの道具というより", "【定義】決め文と同時に一行を提示",
              telop="語録＝仲間を見分ける合言葉"),
        img("僕がまだ仲間じゃなかったから", 7, "circle_outsider", "【仲間の実感】輪の絵に戻り、決め文の余韻の直後から通じ合う嬉しさの話へ"),
        img("なぜ、よりによって", 8, "whisper", "【次章への問い】ひそひそ話の絵に戻り、タブーの話へつなぐ"),
    ],
    5: [
        chapter(),
        img(None, 1, "friends_laugh", "【人はどういうときに笑うのか】友人同士で笑っている数人を直接描写。良性侵犯理論の説明に入る前まで保持（ill_headphones_nightは決め文の後で使う）"),
        diagram(
            "何かの決まりが破られていると感じて",
            "【良性侵犯理論】規則違反と安全の両立が笑いへ収束することをconvergeで示す。決め文「人は笑うの」の間1.5秒まで保持（保持52秒が長すぎたため前振りをimageビートへ譲る）",
            {
                "type": "narrative",
                "layout": "converge",
                "items": [
                    {"id": "broken", "text": "決まりが破られる", "at": "何かの決まりが破られていると感じて", "after": "何かの決まりが破られていると感じて"},
                    {"id": "safe", "text": "自分は傷つかない", "at": "自分は傷つかない、と同時に感じたとき", "after": "自分は傷つかない、と同時に感じたとき"},
                ],
                "result": {"text": "笑いが起きる", "at": "笑いが起きるの", "after": "笑いが起きるの"},
            },
        ),
        img("だから、普通の台詞より", 2, "shape_wall", "【つなぎ】壁の絵に先取りで替え、合言葉の強さの話を続ける"),
        img("単純接触効果と呼ばれる現象よ", 3, "headphones", "【単純接触効果の出典】夜の部屋の絵に戻り、Zajonc 1968の提示へ"),
        img("何百回も聞いているうちに", 4, "shape_wall", "【単純接触効果】壁一面の反復図形で『見るほど馴染む』を比喩化"),
        img("何百回も触れるには", 5, "headphones", "【次章への問い】夜の部屋の絵に戻り、場所の話へつなぐ"),
    ],
    6: [
        chapter(),
        img(None, 1, "nico_comments", "【擬似同期】コメント可視化でニコニコ動画特有の疑似同期を再現（線のみ）。章の開始から保持"),
        img("一つは、動画の上に視聴者のコメントが流れること", 2, "nico_comments", "【間】同じ絵のまま、擬似同期の説明を続ける（保持28秒を短縮するため分割）"),
        img("もう一つは、誰かの作った動画を、別の誰かが切り貼りして", 3, "typing_hands", "【N次創作へ先出し】もう一つの仕組み（N次創作）の絵に替え、「淫夢の素材は」まで保持"),
        diagram(
            "部品を組み合わせた動画が上がり",
            "【N次創作の循環】動画化→合言葉拡散→再制作の3項をchainで見せ、captionで循環を明示（保持39秒が長すぎたため、素材の切り出し・N次創作の紹介は直前のimageビートへ譲り図解を短縮）",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "made", "text": "動画が上がる", "icon": "movie_creation", "at": "部品を組み合わせた動画が上がり", "after": "部品を組み合わせた動画が上がり"},
                    {"id": "comment", "text": "合言葉が流れる", "icon": "chat", "at": "その上にコメントで合言葉が流れ", "after": "その上にコメントで合言葉が流れ"},
                    {"id": "remake", "text": "また誰かが作る", "icon": "replay", "at": "それを見た人がまた部品を組み合わせる", "after": "それを見た人がまた部品を組み合わせる"},
                ],
                "caption": {"text": "また最初に戻る", "at": "この輪が、何年も回り続けたの", "after": "この輪が、何年も回り続けたの"},
            },
        ),
        img("みんなで書き込んで", 3, "typing_hands", "【決め文の保持】大量の手のイラストで参加の多さを示し、決め文の間1.5秒を保持"),
        img("これで、あなたの最初の疑問には答えが出たわ", 4, "nico_comments", "【問いへの回収】コメント可視化に戻り、最初の疑問への答えを示す"),
        img("ただ、ここまでは、熱狂する側から見た話なの", 5, "typing_hands", "【転換】書き込む手の絵に替え、傷つく側への転換を示す"),
    ],
    7: [
        chapter(),
        img(None, 1, "circle_laugh_turned", "【偏見規範理論】笑いが作る空気を、輪から離れる人の絵で示す。章の開始から保持"),
        img("もともと偏見を持っていた人は", 2, "circle_laugh_turned", "【間】同じ絵のまま、偏見が行動に出る話へ切り替えて尺を分ける"),
        img("これを示したのは", 2, "circle_laugh_turned", "【出典の提示】同じ絵のまま、Ford & Fergusonの提唱を示す（研究者肩書き追加で伸びた分、台本側で2文に分割済み。同じ絵のまま尺を分ける）"),
        img("笑ってる本人に悪気がなくても", 3, "circle_laugh_turned", "【間】同じ絵のまま、悪気の有無の話へ"),
        img("悪気の有無とは別に", 4, "protest", "【外への聞こえ方】抗議のプラカードを持つ人々の写真を挟み、批判の具体像を示す（ill_laugh_circle_backの3連続を崩す）"),
        img("使っている側は", 5, "circle_laugh_turned", "【間】同じ絵のまま、当事者からの批判へ"),
        img("合言葉のつもりが", 6, "circle_laugh_turned", "【間】同じ絵のまま、外から見た聞こえ方の結びへ"),
        img("普通の人たちよ", 7, "famous_face", "【出演者は実在する】黒線入り静止画を短く再掲（出所テロップ再掲）",
            telop="© COAT Corporation（2001）より。引用"),
        img("本人は、この文化に参加していない", 8, "circle_laugh_turned", "【被害の継続】同じ絵に戻り、特定・迷惑行為の話へ"),
        img("ビリー・ヘリントンというアメリカの俳優よ", 9, "herrington_portrait", "【本人の実写】ヘリントン本人の写真（ユーザー提供。胸から上でトリミング、クレジット表記あり）"),
        img("ファンのイベントに何度も出た", 10, "fan_event_back", "【ファンイベント】後ろ姿でファンの歓待を描写に戻す（顔なし）"),
        diagram(
            "同じ切り貼りなのに、片方は本人が",
            "【ヘリントン対比】選択の有無と結果を見出し行＋2行の3行2列で対比し、決め文の間2.0秒まで保持",
            sketch(
                [
                    [
                        cell("h0", text="ビリー・ヘリントン", icon="person", at="同じ切り貼りなのに、片方は本人が"),
                        cell("p0", text="淫夢の出演者", icon="person_off", at="同じ切り貼りなのに、片方は本人が"),
                    ],
                    [
                        cell("h1", text="自分で選んで表に出た", at="自分から表に出てきた", after="自分から表に出てきた"),
                        cell("p1", text="選んでいない", at="自らの意思では表に出てきていないのに捜索されたりしている", after="自らの意思では表に出てきていないのに捜索されたりしている"),
                    ],
                    [
                        cell("h2", text="来日・イベント出演", at="同じ切り貼りなのに、片方は本人が"),
                        cell("p2", text="探し出される", at="同じ切り貼りなのに、片方は本人が"),
                    ],
                ],
                arrows=[("h1", "h2"), ("p1", "p2")],
                highlight={"ids": ["p1", "p2"], "at": "自らの意思では表に出てきていないのに捜索されたりしている", "after": "自らの意思では表に出てきていないのに捜索されたりしている"},
                caption={"text": "同じ切り貼り、違う経緯", "at": "同じ切り貼りなのに、片方は本人が"},
            ),
        ),
    ],
    8: [
        img(None, 1, "comment_top", "【冒頭への予告】結びの前振り。コメント欄の再現から始める"),
        board("切り貼りしやすい形をしていたこと", "【結びの整理】ずんだもんの4点列挙をチョーク文字の番号付きで残す",
              telop="熱狂の正体は合言葉の仕組み\n①切り貼りしやすい形 ②通じれば仲間\n③安全に触れるタブー ④何百回も触れる場所"),
        img("その通りよ", 2, "comment_top", "【冒頭への回収】コメント欄の再現に戻り、決め文の仕組みの話へ"),
        img("だから、あなたが次に", 3, "comment_top", "【間】同じ絵のまま、三つの留保へ話を進める"),
        img("その声は、外からは同性愛を笑う声に聞こえうる", 4, "comment_top", "【間】同じ絵のまま、決め文の間2.5秒まで保持"),
        img("笑うのをやめろ", 3, "dark_room_phone", "【最後の一枚】暗い部屋でスマホを見る後ろ姿。アウトロまで保持"),
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
