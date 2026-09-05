"""ずんだもん版・冷笑: ビート（貼り写真 / 黒板のみ / 章カード / チョーク図解）と追加 readings を
YAML に貼り直す。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（ドパガキ版 apply_beats.py と同じ方式）。

  .venv\\Scripts\\python.exe scripts/20260905-cynicism-kamishibai/apply_beats.py

前提: tools/kamishibai_md_to_yaml.py で YAML（narration 部）を生成済み。
貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-cynicism/scene_NN_beat{slot}.*`。

図解の方針（2026-09-05 ユーザー指示「見せたい図のイメージが先、型は後」）: 実験は「誰に→何をした→結果（数字）」の格子、
二群の違いは左右 2 列、用語は言葉＋ピクトグラムを `sketch` で組む。放射・収束は関係そのものを見せたい箇所だけ。
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

YAML_PATH = Path(__file__).with_name("20260905-cynicism-kamishibai.yaml")

# 出典表記（字幕帯右下）。キー = 写真の種類。
CREDIT = {
    "train": "Photo: MART PRODUCTION / Pexels",
    "reply": "Photo: RDNE Stock project / Pexels",
    "agora": "Photo: Uiliam Nörnberg / Pexels",
    "gerome": "Jean-Léon Gérôme, Diogenes (1860), Walters Art Museum / Public Domain",
    "lamp": "Photo: Ravi Kant / Pexels",
    "jar": "Photo: Jan van der Wolf / Pexels",
    "alexander": "Photo: Pixabay",
    "dog": "Photo: Trần Chính / Pexels",
    "delphi": "Photo: Konstantinos Livadas / Pexels",
    "waterhouse": "John William Waterhouse, Diogenes (1882), Art Gallery of NSW / Public Domain",
    "dictionary": "Photo: Pixabay",
    "office": "Photo: AlphaTradeZone / Pexels",
    "fundraiser": "Photo: RDNE Stock project / Pexels",
    "meeting": "Photo: cottonbro studio / Pexels",
    "election": "Photo: Israyosoy S. / Pexels",
    "aesop": "Milo Winter, The Aesop for Children (1919) / Public Domain",
    "veg": "Photo: Garley Gibson / Pexels",
    "lab": "Photo: Sóc Năng Động / Pexels",
    "lab2": "Photo: Pixabay",
    "bulletin": "Photo: Arthur Krijgsman / Pexels",
    "poppy": "Photo: Susanne Jutzeler, suju-foto / Pexels",
    "beach": "Photo: Thirdman / Pexels",
    "exam": "Photo: Kaboompics.com / Pexels",
    "payslip": "Photo: Kaboompics.com / Pexels",
    "chair": "Photo: cottonbro studio / Pexels",
    "outside": "Photo: Hayk Paytyan / Pexels",
    "tv": "Photo: Caleb Oquendo / Pexels",
    "angry": "Photo: Kaboompics.com / Pexels",
    "diet": "Photo: Guohua Song / Pexels",
    "report": "Photo: RDNE Stock project / Pexels",
    "laptop": "Photo: Thirdman / Pexels",
    "thumb": "Photo: Towfiqu barbhuiya / Pexels",
}

# 「嗤」は VOICEVOX の辞書に無く、未登録の活用形は読み飛ばされる（「嗤って」→「ッテ」）。
# 台本に出る全活用形を、その形が本文に含まれるシーンへ登録する。
GLOBAL_READINGS = [
    ("嗤って", "ワラッテ"), ("嗤った", "ワラッタ"), ("嗤っていた", "ワラッテイタ"), ("嗤う", "ワラウ"), ("嗤い", "ワライ"),
    ("嗤いながら", "ワライナガラ"), ("嗤われる", "ワラワレル"), ("嗤われない", "ワラワレナイ"), ("嗤えば", "ワラエバ"),
    ("嗤われ", "ワラワレ"), ("嗤え", "ワラエ"),
]
# 元 YAML（ナレーション版）から転記されない読み。(surface, reading) をシーンに追加する。
EXTRA_READINGS = {
    1: [("口の端", "クチノハ")],
    4: [("甕", "カメ")],
    7: [("無力感", "ムリョクカン")],   # VOICEVOX が「ムリキカン」と読む（v2 ASR チェックで発見。辞書 priority 10 で登録）
    9: [("無力感", "ムリョクカン")],
    12: [("無力感", "ムリョクカン")],
    14: [("甕", "カメ"), ("無力感", "ムリョクカン")],
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
    if text:
        c["text"] = text
    if value:
        c["value"] = value
    if after:
        c["after"] = after
    return c


def sketch(rows, arrows=None, caption=None, highlight=None):
    spec = {"type": "sketch", "rows": rows}
    if arrows:
        spec["arrows"] = [{"from": a, "to": b} for a, b in arrows]
    if caption:
        spec["caption"] = caption
    if highlight:
        spec["highlight"] = highlight
    return spec


BEATS = {
    1: [
        img(None, 1, "train", "【昼の電車】肩越しに見るスマホの画面。冒頭の場面をそのまま"),
        img("返信も見て", 2, "reply", "【返信欄】返信の並ぶ画面を見る手元（別カット）"),
        board("そういう態度のことを、冷笑って呼ぶのよ", "【定義】写真をはずし、黒板に冷笑の定義を書く",
              telop="冷笑＝本気を、一段高いところから鼻で笑って済ませる態度"),
    ],
    2: [
        board(None, "【冷笑系】写真なし。二人だけで言葉の来歴に入る"),
        img("この言葉は、およそ2400年前", 1, "agora", "【古代ギリシャ】アテナイの遺跡へ切り替え"),
        board("なぜ人は、冷笑をしてしまうのか", "【問いの提示】写真をはずし、黒板に問いだけ",
              telop="なぜ人は、冷笑してしまうのか"),
    ],
    3: [
        chapter(),
        img(None, 1, "gerome", "【ランプの男】ジェローム「ディオゲネス」。ランプ・甕・犬が一枚に",
            telop="ディオゲネス・ラエルティオス『ギリシア哲学者列伝』第6巻"),
        img("真昼にランプ？", 2, "lamp", "【火のついたランプ】素焼きのランプの実写"),
        img("甕の中で寝てたのだ", 3, "jar", "【素焼きの甕】大きな貯蔵用の甕"),
        img("ある日、アレクサンドロス大王", 4, "alexander", "【大王】アレクサンドロス大王の彫像"),
        img("人々は彼を、「犬」と呼んだの", 5, "dog", "【犬】屋外の犬"),
        img("もうひとつ、神託の話があるわ", 6, "delphi", "【神託】デルフォイの遺跡"),
        board("という呼び名がシニシズムの語源", "【決め文】写真をはずし、語源を黒板に",
              telop="犬（キュオーン）→ シニシズム"),
    ],
    4: [
        img(None, 1, "waterhouse", "【犬のような者たち】ウォーターハウス「ディオゲネス」",
            telop="キュオーン（犬）→ キュニコス（犬のような者たち）→ Cynic"),
        board("フランスの哲学者ミシェル・フーコー", "【真理の勇気】写真をはずし、出典を黒板に",
              telop="Foucault『真理の勇気』（1983-84 講義）／ Mazella (2007)"),
        diagram("ディオゲネスは、富や資産を", "【対比: 昔の犬と今の冷笑】嗤う対象の違いを左右 2 列で見せる（ずんだもんの「下から上？」への答え）",
                sketch([[cell("old", "昔の犬", "pets", at="ディオゲネスは、富や資産を"),
                         cell("old_t", "持つ側を嗤う", "account_balance", at="ディオゲネスは、富や資産を", after="人々を嗤った")],
                        [cell("now", "今の冷笑", "sentiment_dissatisfied", at="今の冷笑は、自分から行動する"),
                         cell("now_t", "行動する側を嗤う", "directions_run", at="今の冷笑は、自分から行動する", after="人々を嗤うの")]],
                       arrows=[("old", "old_t"), ("now", "now_t")])),
        img("冷笑という言葉はやがて意味を変えるの", 2, "dictionary", "【19世紀の語義】古い辞書のページ（文字は読めない）"),
        diagram("英語のシニックが", "【図解: 反転の三証言】近代の冷笑を中心に、19世紀の語義・マゼラ・スローターダイクの三つが放射し、決め文で色が転じる（状態変化が主張）",
                {"type": "narrative", "layout": "radiate",
                 "center": {"icon": "psychology", "text": "近代の冷笑", "at": "英語のシニックが"},
                 "items": [
                     {"id": "motive", "text": "動機を疑って嗤う", "at": "英語のシニックが", "after": "鼻で笑う性格"},
                     {"id": "mazella", "text": "鍛錬から無関心へ", "at": "昔は欲望を抑える鍛錬だったものが"},
                     {"id": "sloterdijk", "text": "知っていて動かない", "at": "近代の、知っていながら動かない態度が"},
                 ],
                 "turn": {"at": "今の冷笑は、本気に吠えている"}}),
    ],
    5: [
        chapter(),
        img(None, 1, "fundraiser", "【寄付を集める箱】CHARITY の札と寄付箱",
            telop="津田正太郎（慶應義塾大学）現代ビジネス"),
        diagram("「あの人はカネのためにやっている」", "【言葉: 三つの決めつけ】三つの言葉をピクトグラム付きで並べる。写真をはずして黒板に",
                sketch([[cell("k1", "カネのため", "payments", at="「あの人はカネのためにやっている」", after="カネのため"),
                         cell("k2", "売名だ", "campaign", at="「あの人はカネのためにやっている」", after="売名だ"),
                         cell("k3", "ポーズだ", "theater_comedy", at="「あの人はカネのためにやっている」", after="ポーズだ")]],
                       caption={"text": "動機を疑えば、考えずに済む", "at": "こう決めてしまえば"})),
        diagram("批判する側も、擁護する側も", "【対比: 敵同士が同じことをする】両側から中央の決めつけへ矢印",
                sketch([[cell("a", "批判する側", "person", at="批判する側も、擁護する側も", after="批判する側"),
                         cell("m", "邪悪な動機だと決めつけ", "gavel", at="批判する側も、擁護する側も", after="邪悪な動機がある"),
                         cell("b", "擁護する側", "person", at="批判する側も、擁護する側も", after="擁護する側")]],
                       arrows=[("a", "m"), ("b", "m")])),
        board("冷笑の第一の安さは", "【決め文】黒板に第一の安さ", telop="第一の安さ：考えなくて済む"),
    ],
    6: [
        img(None, 1, "meeting", "【腕を組んで見ている人】会議室で椅子にもたれる後ろ姿",
            telop="Stavrova & Ehlebracht (2019) PSPB"),
        diagram("同じ質問を、オランダの", "【実験: 674 人の答え】質問 → 多数派の答えと割合",
                sketch([[cell("q", "674人に質問", "groups", at="同じ質問を、オランダの", after="674人"),
                         cell("a", "皮肉屋が賢い", "psychology", at="調べ方によって、56パーセント", after="56パーセント", value="56〜70%")]],
                       arrows=[("q", "a")])),
        board("しかも、その「賢そう」という印象は", "【決め文】第二の安さ", telop="第二の安さ：何もしなくても賢い側に立てる"),
        diagram("ただ、この研究には、続きがあるのよ", "【言葉: 見える／本当か】次章への引きを 2 語で",
                sketch([[cell("look", "賢く見える", "visibility", at="ただ、この研究には、続きがあるのよ"),
                         cell("real", "本当に賢い？", "help", at="皮肉屋は本当に賢かったのだ")]])),
    ],
    7: [
        chapter(),
        diagram(None, "【図解: 三つの安さ】前章の二つに三つ目が加わり「冷笑は安い」へ収束する（構造が主張）",
                {"type": "narrative", "layout": "converge",
                 "items": [
                     {"id": "think", "text": "考えなくて済む", "at": 1},
                     {"id": "smart", "text": "賢く見える", "at": 1},
                     {"id": "guard", "text": "自分を守れる", "at": 1, "after": "防衛の安さよ"},
                 ],
                 "result": {"text": "冷笑は安い", "at": "つまり冷笑は、何かから"}}),
        img("日本財団が2019年に行った", 1, "election", "【日本の若者】選挙ポスターの前を歩く人々",
            telop="「自分で国や社会を変えられる」日本 18.3%（9カ国中最下位）"),
        board("と思っていると、変えようとする人まで", "【前提】写真をはずし、前提を黒板に", telop="「どうせ変わらない」→ 変えようとする人が愚か者に見える"),
        img("哲学者のヤン・エルスターは", 2, "aesop", "【酸っぱい葡萄】ナレーション自身の比喩を PD 挿絵で"),
        diagram("社会なんて変えられないと思うと", "【対比: 狐と冷笑は同じ形】葡萄→酸っぱいことにする／社会→変えようとする人を嗤う",
                sketch([[cell("g1", "届かない葡萄", "nutrition", at="社会なんて変えられないと思うと"),
                         cell("g2", "酸っぱいことにする", "sentiment_dissatisfied", at="社会なんて変えられないと思うと")],
                        [cell("s1", "変えられない社会", "public", at="社会なんて変えられないと思うと", after="変えられないと思うと"),
                         cell("s2", "変えようとする人を嗤う", "sentiment_very_dissatisfied", at="社会なんて変えられないと思うと", after="嗤ってしまうことがある")]],
                       arrows=[("g1", "g2"), ("s1", "s2")],
                       caption={"text": "動かない自分を責めずに済む", "at": "そうすると、動かない自分を責めずに済むのよ"})),
    ],
    8: [
        img(None, 1, "veg", "【ベジタリアン】野菜の食卓", telop="Minson & Monin (2012) SPPS"),
        diagram("すると47パーセントの人が", "【実験: 善行者への貶め】肉を食べる人→連想→否定 47%。2 行目に予期→貶める",
                sketch([[cell("p", "肉を食べる人", "restaurant", at="すると47パーセントの人が"),
                         cell("c", "ベジタリアンを連想", "psychology_alt", at="すると47パーセントの人が"),
                         cell("r", "否定的な言葉", "thumb_down", at="すると47パーセントの人が", after="否定的な言葉", value="47%")],
                        [cell("e", "見下されているはず", "visibility_off", at="とくに否定的だった人ほど"),
                         None,
                         cell("d", "相手を貶める", "trending_down", at="「そう思われそう」と感じただけで", after="貶めてしまうの")]],
                       arrows=[("p", "c"), ("c", "r"), ("e", "d")],
                       caption={"text": "善行者への貶め", "at": "研究チームはこれを"})),
        img("2008年の実験では、もっとはっきり", 2, "lab", "【2008年の実験】実験室で課題に向かう参加者の後ろ姿",
            telop="Monin, Sawyer & Marquez (2008) JPSP"),
        diagram("でも、その場に関係のない第三者は", "【実験: 非対称】同じ課題をやった人→嫌った／第三者→好んだ",
                sketch([[cell("s", "同じ課題をやった人", "groups", at="でも、その場に関係のない第三者は"),
                         cell("h", "断った人を嫌った", "heart_broken", at="でも、その場に関係のない第三者は")],
                        [cell("t", "関係のない第三者", "person_search", at="でも、その場に関係のない第三者は", after="第三者は"),
                         cell("l", "断った人を好んだ", "favorite", at="でも、その場に関係のない第三者は", after="好んだの")]],
                       arrows=[("s", "h"), ("t", "l")],
                       caption={"text": "自分も問われた人だけが嫌う", "at": "正しいことをした人が気に障るのは"})),
        img("ここで、冒頭の画面に戻って", 3, "train", "【冒頭の再演】電車のスマホ画面を再掲"),
        board("この実験で嫌われたのは", "【決め文】写真をはずし、二人だけで"),
    ],
    9: [
        img(None, 1, "lab2", "【映像を見る参加者】モニターの前の後ろ姿", telop="Smith et al. (1996) PSPB"),
        diagram("誰がその挫折を喜ぶか", "【実験: 挫折を喜ぶのは誰か】映像→挫折を伝える→嫉妬していた人ほど喜ぶ",
                sketch([[cell("v", "優秀な学生の映像", "school", at="誰がその挫折を喜ぶか"),
                         cell("f", "挫折したと伝える", "trending_down", at="誰がその挫折を喜ぶか"),
                         cell("j", "嫉妬していた人ほど喜ぶ", "mood", at="結果は、優秀さへの嫉妬を", after="喜んだの")]],
                       arrows=[("v", "f"), ("f", "j")])),
        img("オーストラリアのフリンダース大学", 2, "bulletin", "【高く昇った人】前方の画面を見る生徒たち",
            telop="Feather (1989)／Feather & Sherman (2002)"),
        img("オーストラリアには、「高く伸びた芥子", 3, "poppy", "【高く伸びた芥子】一本だけ高い花。ナレーション自身の比喩",
            telop="高く伸びた芥子は刈り取られる（Tall Poppy）"),
        board("自分と似た立場の誰かが", "【決め文】写真をはずし、棘の出どころを聞かせる"),
        diagram("フェザーが2002年に行った実験では", "【対比: 嫉妬か憤りか】予測したのは憤り。ずんだもんの復唱で憤りが点灯",
                sketch([[cell("envy", "嫉妬", "mood_bad", at="フェザーが2002年に行った実験では", after="嫉妬そのものより"),
                         cell("unfair", "不当だという憤り", "gavel", at="フェザーが2002年に行った実験では", after="憤りだったわ")]],
                       caption={"text": "転落を喜ぶ気持ちを予測したのは", "at": "フェザーが2002年に行った実験では"},
                       highlight={"ids": ["unfair"], "at": "不当だ、という気持ち"})),
    ],
    10: [
        board(None, "【一枚の地図】写真なし。フィスクの二軸を言葉で導入", telop="Fiske, Cuddy, Glick & Xu (2002) JPSP"),
        diagram("「有能だけど冷たい」と見られた相手には", "【対比: 二軸の二つの組】有能で冷たい→妬み／無能で冷たい→軽蔑",
                sketch([[cell("a1", "有能で冷たい", "workspace_premium", at="「有能だけど冷たい」と見られた相手には"),
                         cell("a2", "妬み", "sentiment_very_dissatisfied", at="「有能だけど冷たい」と見られた相手には", after="妬みが")],
                        [cell("b1", "無能で冷たい", "block", at="じゃあ、無能で冷たいと思われた相手は"),
                         cell("b2", "軽蔑", "thumb_down", at="ええ、軽蔑が向くわ", after="軽蔑")]],
                       arrows=[("a1", "a2"), ("b1", "b2")],
                       caption={"text": "温かさ×有能さ（Fiske 2002）", "at": "「有能だけど冷たい」と見られた相手には"})),
        img("本気で何かを変えようとする人は、まだ成果が", 1, "beach", "【ボランティア】水辺でごみを拾う人々（遠景）。冒頭の投稿の中身"),
        diagram("標的は違っても", "【図解: 三つの防衛】無力感・責められる予期・不当だという感覚が「自分を守るための反応」へ収束する",
                {"type": "narrative", "layout": "converge",
                 "items": [
                     {"id": "power", "text": "無力感", "at": "標的は違っても"},
                     {"id": "blame", "text": "責められる予期", "at": "標的は違っても"},
                     {"id": "unfair", "text": "不当だという感覚", "at": "標的は違っても"},
                 ],
                 "result": {"text": "自分を守るための反応", "at": "どれも、自分を守るための反応だ"}}),
    ],
    11: [
        chapter(),
        img(None, 1, "exam", "【認知課題】読解・数学のテストに向かう手元", telop="Stavrova & Ehlebracht (2019) PSPB"),
        board("結果は、逆だったのよ", "【反転】写真をはずして間", telop="皮肉屋の天才幻想（cynical genius illusion）"),
        diagram("皮肉の強い人ほど、読解や数学の", "【対比: 予想と実際】皮肉屋が賢い 56〜70% ／ 成績は低い 30カ国。実際が点灯",
                sketch([[cell("pred", "予想: 皮肉屋が賢い", "psychology", at="皮肉の強い人ほど、読解や数学の", value="56〜70%"),
                         cell("real", "実際: 成績は低い", "school", at="皮肉の強い人ほど、読解や数学の", after="低かったの", value="30カ国")]],
                       highlight={"ids": ["real"], "at": "相関は弱いけれど、30カ国で"})),
        img("同じチームがアメリカの全国調査", 2, "payslip", "【9年後の収入】明細と財布を持つ手元",
            telop="Stavrova & Ehlebracht (2016) JPSP"),
        img("2024年には、もっと切ない結果", 3, "chair", "【リーダーに選ばれない】会議室の机の端",
            telop="Stavrova, Ehlebracht & Ren (2024) British Journal of Psychology"),
        img("仲間はずれの実験もあるのよ", 4, "outside", "【つながり直せない】集団に背を向けて立つ一人",
            telop="Choy, Eom & Li (2021) Personality and Individual Differences"),
        diagram("傷つく前に切り捨てるから", "【請求書: 四つの代価】ここまで一枚ずつ見せた項目を 2×2 で一望にする",
                sketch([[cell("c1", "認知能力", "school", at="傷つく前に切り捨てるから", value="低い"),
                         cell("c2", "9年後の収入", "payments", at="傷つく前に切り捨てるから", value="低い")],
                        [cell("c3", "リーダー", "groups", at="傷つく前に切り捨てるから", value="選ばれない"),
                         cell("c4", "つながり直せない", "link_off", at="傷つく前に切り捨てるから")]],
                       caption={"text": "安い知性の請求書", "at": "傷つく前に切り捨てるから"})),
        board("精神科医のジョージ・ヴァイラント", "【防衛の成熟度】黒板に二つの防衛",
              telop="ユーモア＝成熟した防衛／受動攻撃＝未成熟な防衛（Vaillant）"),
        board("冷笑は安い", "【決め文1】", telop="冷笑は安い"),
        board("でも、安いものはたいてい", "【決め文2】", telop="安いものには、後で請求書が来る"),
    ],
    12: [
        chapter(),
        img(None, 1, "tv", "【勝ち負けの報道】テレビスタジオ", telop="Cappella & Jamieson (1997) Spiral of Cynicism"),
        board("32の研究、およそ", "【メタ分析】写真をはずし、数字を黒板に",
              telop="戦略報道 → シニシズム（メタ分析 2021・32研究・約3万9000人）"),
        img("SNSには別の道筋もあるわ", 2, "angry", "【攻撃投稿と怒り】スマホを握る手元",
            telop="Hasell, Halversen & Weeks (2025) 2020年米大統領選パネル"),
        diagram("画面を開くたびに", "【実験: 攻撃投稿→怒り→シニシズム】1800 人の追跡で見つかった経路",
                sketch([[cell("see", "攻撃投稿を見る", "smartphone", at="画面を開くたびに"),
                         cell("anger", "怒り", "local_fire_department", at="画面を開くたびに"),
                         cell("cyn", "シニシズム", "sentiment_dissatisfied", at="画面を開くたびに")]],
                       arrows=[("see", "anger"), ("anger", "cyn")],
                       caption={"text": "冷笑は環境の産物でもある", "at": "冷笑は、性格である前に"})),
        img("政府への信頼は", 3, "diet", "【政府への信頼】国会議事堂",
            telop="政府への信頼 24%（OECD 2021）／社会を変えられる 18.3%"),
        board("日本で目立つのは", "【決め文】写真をはずす", telop="日本は「不信の国」ではなく「無力感の国」"),
        diagram("似た無力感は、ずっと前から", "【年表: 半世紀の系譜】1972 連合赤軍事件 → 三無主義 → 2005 皮肉な共同体",
                sketch([[cell("y1", "連合赤軍事件", "history", at="1972年の連合赤軍事件", value="1972"),
                         cell("y2", "三無主義", "bedtime", at="若者の無気力、無関心、無責任は", value="1970年代"),
                         cell("y3", "皮肉な共同体", "forum", at="社会学者の北田暁大さん", value="2005")]],
                       caption={"text": "形を変えながら続く半世紀の系譜", "at": "冷笑には、形を変えながら続く"})),
    ],
    13: [
        img(None, 1, "report", "【懐疑＝道具】資料を読み込み付箋を貼る手", telop="Citrin & Stoker (2018) Annual Review of Political Science"),
        diagram("制度を見張る懐疑は", "【言葉: 見張る／見放す】二種類の不信を 2 語で",
                sketch([[cell("sk", "懐疑＝制度を見張る", "search", at="制度を見張る懐疑は"),
                         cell("cy", "シニシズム＝見放す", "block", at="というシニシズムに変わったら")]])),
        diagram("認知能力の高い人は", "【対比: 疑うべきときに疑う／いつも疑う】スタヴロヴァの二群。caption で道具と癖に着地",
                sketch([[cell("hi", "認知能力が高い", "school", at="認知能力の高い人は"),
                         cell("hi2", "腐敗の多い社会でだけ疑う", "search", at="認知能力の高い人は", after="強めていたの")],
                        [cell("lo", "認知能力が低い", "person", at="一方、認知能力の低い人は"),
                         cell("lo2", "いつもシニカル", "repeat", at="一方、認知能力の低い人は", after="強かったのよ")]],
                       arrows=[("hi", "hi2"), ("lo", "lo2")],
                       caption={"text": "懐疑（道具）／ 冷笑（癖）", "at": "疑いが、状況を見て使う道具ではなく"})),
        img("……癖だったのだ", 2, "laptop", "【癖】ノートPCに手を置く"),
        diagram("スタンフォード大学の心理学者、ジャミール・ザキ", "【言葉: 希望を持った懐疑】主張は疑う／人が変わる力は疑わない",
                sketch([[cell("d", "主張は疑う", "fact_check", at="主張は疑う"),
                         cell("h", "人が変わる力は疑わない", "favorite", at="人が変わる力までは")]],
                       caption={"text": "希望を持った懐疑（Zaki 2024）", "at": "スタンフォード大学の心理学者、ジャミール・ザキ"})),
    ],
    14: [
        img(None, 1, "gerome", "【回帰】ランプの男へ戻る"),
        board("安全な場所から、何も賭けずに", "【削られるもの】写真をはずし、二人だけで"),
        img("もう一度思い出してみて", 2, "train", "【冒頭へ回帰】電車のスマホ画面を再掲"),
        board("冷笑は安い", "【決め文】写真をはずし、決め文を黒板で受ける", telop="冷笑は安い。だから、広がる"),
        img("傷つきたくない気持ちなのよ", 3, "thumb", "【最後の一枚】暗がりで光る画面に指を置く手。決め文と同時に出し、余韻とアウトロで保持"),
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
                b["slot"] = slot
                b["credit"] = CREDIT[ckey]
            if kind == "diagram":
                b["diagram"] = resolve_ats(telop, cues, sid)
            elif telop:
                b["telop"] = telop
            beats.append(b)
        scene["beats"] = beats
        total += len(beats)
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
