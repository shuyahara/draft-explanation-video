"""ずんだもん版・ルッキズム: ビート（貼り写真 / 章カード / チョーク図解）と追加 readings を
YAML に貼り直す。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（冷笑版 apply_beats.py と同じ方式）。

  .venv\\Scripts\\python.exe scripts/20260906-lookism-kamishibai/apply_beats.py

前提: tools/kamishibai_md_to_yaml.py で YAML（narration 部）を生成済み。
貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-lookism/scene_NN_beat{slot}.jpg`。

図解の方針（2026-09-05 ユーザー指示「見せたい図のイメージが先、型は後」）: 実験は「誰に→何をした→結果（数字）」の格子、
二群の違いは左右2列、賃金差の唯一の chart、因果の一本鎖は chain、結論への収束は converge（items は4件まで）。
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

YAML_PATH = Path(__file__).with_name("20260906-lookism-kamishibai.yaml")

# 出典表記（字幕帯右下）。キーは写真1枚ごと（同じ写真をシーン内で連続使用しないため、
# カテゴリ内の候補3枚を使い分ける。manifest.md 記載の作者・ライセンスに基づく）。
CREDIT = {
    "ringlight1": "Photo: Liza Summer / Pexels",
    "ringlight2": "Photo: George Milton / Pexels",
    "ringlight3": "Photo: Pixabay",
    "phone1": "Photo: Pixabay",
    "phone2": "Photo: Pixabay",
    "phone3": "Photo: Jakub Zerdzicki / Pexels",
    "night1": "Photo: Pixabay",
    "night2": "Photo: Beyza Kaplan / Pexels",
    "night3": "Photo: Ericson Fernandes / Pexels",
    "bookstore1": "Photo: Eden Constantino / Pexels",
    "bookstore2": "Photo: Serra Nur Çevikdal / Pexels",
    "bookstore3": "Photo: wal_172619 / Pexels",
    "dictionary1": "Photo: Tima Miroshnichenko / Pexels",
    "crowd1": "Photo: Elina Sazonova / Pexels",
    "crowd2": "Photo: Francesco Rosati / Pexels",
    "crowd3": "Photo: Pixabay",
    "portrait1": "Photo: John Barnard / Pexels",
    "portrait2": "Photo: Valeria Boltneva / Pexels",
    "portrait3": "Photo: Râmbeț Ioana / Pexels",
    "paycheck1": "Photo: Kaboompics.com / Pexels",
    "paycheck2": "Photo: Towfiqu barbhuiya / Pexels",
    "interview1": "Photo: Kampus Production / Pexels",
    "interview2": "Photo: Pixabay",
    "interview3": "Photo: ANTONI SHKRABA production / Pexels",
    "filter1": "Photo: Mizuno K / Pexels",
    "filter2": "Photo: Pixabay",
    "instagram1": "Photo: Kerde Severin / Pexels",
    "clinic1": "Photo: Marc Chemla / Pexels",
    "clinic2": "Photo: Anna Tarazevich / Pexels",
    "clinic3": "Photo: Max Vakhtbovych / Pexels",
    "mirror1": "Photo: Konna Jpg / Pexels",
    "mirror2": "Photo: cottonbro studio / Pexels",
    "mirror3": "Photo: cottonbro studio / Pexels",
    "streamer1": "Photo: Alpha En / Pexels",
    "streamer2": "Photo: Jakub Zerdzicki / Pexels",
    "streamer3": "Photo: Pixabay",
    "pen1": "Photo: Pixabay",
    "pen2": "Photo: Tima Miroshnichenko / Pexels",
    "pen3": "Photo: Pixabay",
    "scale1": "Photo: Pixabay",
    "scale2": "Photo: Pixabay",
    "scale3": "Photo: Pixabay",
    "closing1": "Photo: Towfiqu barbhuiya / Pexels",
}

# 採用元ファイル（`assets-kamishibai/photos/candidates-lookism/` からの相対パス）。
# render-assets-lookism へコピーする際に使う（このスクリプト自身は参照しない。コピー手順を
# 一箇所にまとめるための対応表）。
SOURCE_FILE = {
    "ringlight1": "youtuber-ringlight/youtuber-ringlight-1.jpg",
    "ringlight2": "youtuber-ringlight/youtuber-ringlight-2.jpg",
    "ringlight3": "youtuber-ringlight/youtuber-ringlight-3.jpg",
    "phone1": "phone-video/phone-video-1.jpg",
    "phone2": "phone-video/phone-video-2.jpg",
    "phone3": "phone-video/phone-video-3.jpg",
    "night1": "night-street/night-street-1.jpg",
    "night2": "night-street/night-street-2.jpg",
    "night3": "night-street/night-street-3.jpg",
    "bookstore1": "bookstore/bookstore-1.jpg",
    "bookstore2": "bookstore/bookstore-2.jpg",
    "bookstore3": "bookstore/bookstore-3.jpg",
    "dictionary1": "dictionary/dictionary-1.jpg",
    "crowd1": "crowd-city/crowd-city-1.jpg",
    "crowd2": "crowd-city/crowd-city-2.jpg",
    "crowd3": "crowd-city/crowd-city-3.jpg",
    "portrait1": "portrait-photos/portrait-photos-1.jpg",
    "portrait2": "portrait-photos/portrait-photos-2.jpg",
    "portrait3": "portrait-photos/portrait-photos-3.jpg",
    "paycheck1": "paycheck-wallet/paycheck-wallet-1.jpg",
    "paycheck2": "paycheck-wallet/paycheck-wallet-2.jpg",
    "interview1": "job-interview/job-interview-1.jpg",
    "interview2": "job-interview/job-interview-2.jpg",
    "interview3": "job-interview/job-interview-3.jpg",
    "filter1": "beauty-filter/beauty-filter-1.jpg",
    "filter2": "beauty-filter/beauty-filter-2.jpg",
    "instagram1": "instagram-scroll/instagram-scroll-1.jpg",
    "clinic1": "cosmetic-clinic/cosmetic-clinic-1.jpg",
    "clinic2": "cosmetic-clinic/cosmetic-clinic-2.jpg",
    "clinic3": "cosmetic-clinic/cosmetic-clinic-3.jpg",
    "mirror1": "mirror-selfcare/mirror-selfcare-1.jpg",
    "mirror2": "mirror-selfcare/mirror-selfcare-2.jpg",
    "mirror3": "mirror-selfcare/mirror-selfcare-3.jpg",
    "streamer1": "streamer-desk/streamer-desk-1.jpg",
    "streamer2": "streamer-desk/streamer-desk-2.jpg",
    "streamer3": "streamer-desk/streamer-desk-3.jpg",
    "pen1": "signing-contract/signing-contract-1.jpg",
    "pen2": "signing-contract/signing-contract-2.jpg",
    "pen3": "signing-contract/signing-contract-3.jpg",
    "scale1": "scale-balance/scale-balance-1.png",
    "scale2": "scale-balance/scale-balance-2.jpg",
    "scale3": "scale-balance/scale-balance-3.jpg",
    "closing1": "closing-symbol/closing-symbol-1.jpg",
}

# 台本「発音・ポーズメモ」に書かれた読み。元 YAML（ナレーション版）に既にあるものは
# 表記が本文に含まれるシーンへ自動転記され（下の V5 読み込みループ）、重複は無視される。
GLOBAL_READINGS = [
    ("日陰", "ヒカゲ"),
    ("多様性", "タヨウセイ"),
    ("偏り", "カタヨリ"),
    ("善い", "ヨイ"),
    ("一割", "イチワリ"),
    ("賃金", "チンギン"),
    ("美顔", "ビガン"),
    ("整形", "セイケイ"),
    ("顔面形成外科医", "ガンメンケイセイゲカイ"),
    ("肩書き", "カタガキ"),
    ("外野", "ガイヤ"),
    ("搾取", "サクシュ"),
    ("値踏み", "ネブミ"),
    ("性産業", "セイサンギョウ"),
    ("選別", "センベツ"),
]
# 元台本（ナレーション版）から転記されない読み。(surface, reading) をシーンに追加する。
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}
# シーン構成・番号は元台本と同じ（S3 削除等の欠番なし）なので、表記が本文に含まれるかで
# 全シーンに転記する（GLOBAL と同じ扱い。手本と同じ仕組み）。
_V5 = Path("C:/Users/shuya/Projects/draft-explanation-video/scripts/20260819-sns-lookism-v6/20260819-sns-lookism-v6.yaml")
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
        img(None, 1, "ringlight1", "【冒頭】リングライトの前で語る元キャバ嬢のユーチューバー（後ろ姿・静止画）"),
        img("フォロワーは何十万人", 2, "phone1", "【視聴】スマホで動画を見る手元へ切り替え"),
        img("二十年くらい前なら", 3, "night1", "【二十年前】夜の路地のネオン（人物は遠景）で「日陰の仕事」の時代へ"),
        img("キャバクラで働くことは", 4, "night2", "【偏見の中身】別アングルのネオンに替えて「夜の世界」「日陰の仕事」を説明"),
        img("ファッションのお手本", 5, "bookstore1", "【いま】書店の平積み（題は読めない）でファッションのお手本として語られる現在へ"),
        img("ねえ、ずんだもん", 6, "bookstore2", "【問い返し】書店の別カットに替えて「どうしてだと思う？」の間へ"),
        img("それだと、何も言っていないのと同じよ", 7, "bookstore3", "【決め文】書店の別カットに替えて「時代が変わったから」のボツへ"),
        img("せっかくだから、心理学と経済学の研究を根拠にして", 8, "bookstore1", "【本題への導入】書店1カット目に戻し研究を根拠にする宣言へ"),
        img("調べていくとね", 9, "bookstore2", "【予告】書店の別カットに替えて外見の評価・お金の話への予告へ"),
    ],
    2: [
        chapter(),
        img(None, 1, "dictionary1", "【定義】「受け入れられている」の意味をそろえる導入。辞書を引く手元",
            telop="受け入れられている＝①隠さず話す人が増えた ②応援される・昔の仕事だけで責められない場面が増えた"),
        img("コメント欄", 2, "phone3", "【現実】きつい言葉も残るコメント欄の代替。TVの前でアプリ画面を持つ手元"),
        img("もう一つは、話した人が応援される", 3, "phone2", "【定義の続き】公園で動画を見る手元に替えて「受け入れられている」の二つ目の意味へ"),
        img("隠さないし、応援してる人が多いのだ", 4, "phone1", "【当てはめ】スマホ画面操作の手元に替えてS1の例が二つとも当てはまる確認"),
        img("多様性の時代になったから", 5, "crowd2", "【よくある説明】「多様性の時代」の街の雑踏（後ろ姿）へ切り替え"),
        img("さっきよりはいい答えよ", 6, "crowd3", "【まだ足りない】雑踏の別カットに替えて「なぜ多様性が」の問い直しへ"),
        img("要因はいくつもあるけれど", 7, "crowd1", "【注目する変化】雑踏の別カットに替えて写真SNS・ルッキズム加速の提示へ",
            telop="注目する変化：写真SNS → 外見が評価や収入につながりやすくなった（ルッキズムの加速）"),
        img("ルッキズムって、見た目で人を判断すること", 8, "crowd2", "【疑問】雑踏1カット目に戻しルッキズムの語義への疑問へ"),
    ],
    3: [
        chapter(),
        img(None, 1, "portrait1", "【ハロー効果】机に並べた人物写真のプリント（顔は小さいか裏返し）"),
        img("たとえば、どういうことなのだ", 2, "portrait3", "【ディオン1972の導入】写真箱の別カットに替えて出典の実験へ",
            telop="出典「Dion, Berscheid & Walster (1972) What Is Beautiful Is Good. JPSP」"),
        diagram(
            "男女60人の大学生に",
            "【実験: ディオン1972】対象→操作→結果を格子で。3列目は温かい・社交的・有能・幸せの順に発話同期",
            sketch(
                [
                    [
                        cell("subj", "大学生60人", icon="school", at="男女60人の大学生に"),
                        cell("op", "顔写真で推測", icon="quiz", at="男女60人の大学生に"),
                        cell("w1", "温かい・社交的", icon="favorite", at="魅力が高い写真の人ほど", after="温かくて社交的で"),
                    ],
                    [None, None, cell("w2", "有能", icon="psychology", at="魅力が高い写真の人ほど", after="能力も高そうだ")],
                    [None, None, cell("w3", "幸せ", icon="celebration", at="幸せな人生を送りそうだ", after="幸せな人生")],
                ],
            ),
        ),
        img("私も、ずんだもんもね", 3, "crowd2", "【日常への引き戻し】街の雑踏（再掲）で「誰でもやってしまう」を示す"),
        img("つまり私たちは、無意識に", 4, "crowd3", "【まとめ】雑踏の別カットに替えて結びつけの一言へ"),
        img("でも、それが世の中を変えるほど大きい力なのだ", 5, "crowd1", "【次章への問い】雑踏の別カットに替えて賃金差への予告へ"),
    ],
    4: [
        chapter(),
        img(None, 1, "paycheck2", "【賃金差の導入】財布から紙幣を取り出す手元",
            telop="出典「Hamermesh & Biddle (1994) Beauty and the Labor Market. AER」"),
        img("容姿と収入……", 2, "paycheck1", "【問い返し】紙幣を数える手元に替えて「給料が高いのだ？」へ"),
        diagram(
            "見た目が平均より良いとされた人は",
            "【chart】ハマーメッシュ&ビドル1994の賃金差。動画で唯一の chart",
            chart(
                "bar",
                source="Hamermesh & Biddle (1994) American Economic Review 84(5), Table 6",
                title="容姿による賃金差",
                unit="%",
                at="一割を超える差になるのよ",
                points=[
                    {"label": "平均以下", "value": -6.9},
                    {"label": "平均", "value": 0.0},
                    {"label": "平均以上", "value": 4.9},
                ],
            ),
        ),
        img("学歴や経験など", 3, "interview2", "【美の経済的プレミアム】統計的に条件を考慮しても差が残る話へ。面接室（後ろ姿）"),
        img("見た目が生きる仕事を選んだから", 4, "interview1", "【sorting】握手の手元に替えて職業選択だけでは説明しきれない点へ"),
        img("キャバ嬢も、その一つなのだ", 5, "interview3", "【接続】握手の別カットに替えてキャバ嬢との関連づけへ"),
        img("じゃあ、SNSの時代になって", 6, "interview2", "【フィルター時代への疑問】面接室に戻し加工で差が消えるかという問いへ"),
        img("美顔フィルターを使って", 7, "filter2", "【追試の導入】Gulati 2024 の美顔フィルター実験。スマホのカメラで撮影する手元（顔なし）",
            telop="出典「Gulati et al. (2024) Royal Society Open Science（ELLIS Alicante ほか・評価者2,748人）」"),
        diagram(
            "加工前と、フィルターをかけた後を",
            "【対比: フィルター前後】写っているのは同じ人なのにで右列（フィルター後）を出す",
            sketch(
                [
                    [
                        cell("before", "加工前の顔写真", icon="photo_camera", at="加工前と、フィルターをかけた後を"),
                        cell("after2", "フィルター後の顔", icon="auto_fix_high", at="写っているのは同じ人なのに", after="写っているのは同じ人なのに"),
                    ]
                ],
                caption={"text": "知性・信頼性が上がる", "at": "知性も信頼性も高く評価されたの"},
            ),
        ),
    ],
    5: [
        chapter(),
        img(None, 1, "instagram1", "【入口】写真中心のSNSを開いたときに最初に目に入るもの。写真グリッドをスクロールする手元",
            telop="出典「Di Gesto et al. (2021) Aesthetic Plastic Surgery（フィレンツェ大学・女性305人・相関研究）」"),
        diagram(
            "最初の判断材料になるのよ",
            "【chain: 写真SNS→整形容認】4項目を「心まで忙しいのだ」までに全部出す。キャプションは関連であり順番の証明ではない旨",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "sns", "text": "写真SNS", "icon": "smartphone", "at": "最初の判断材料になるのよ"},
                    {"id": "compare", "text": "容姿を比べる", "icon": "compare", "at": "他人と容姿を比べやすかったのよ", "after": "容姿を比べやすかった"},
                    {"id": "dissat", "text": "体への不満", "icon": "sentiment_dissatisfied", "at": "自分の体への不満が強かった", "after": "体への不満が強かった"},
                    {"id": "accept", "text": "整形への抵抗が弱い", "icon": "healing", "at": "抵抗も、弱かったのよ", "after": "抵抗も、弱かった"},
                ],
                "caption": {"text": "関連。順番の証明ではない", "at": "順番まで証明したわけではないのよ"},
            },
        ),
        img("医師への調査", 2, "clinic1", "【AAFPRS 会員調査】自撮りのために整形を望む患者増。美容クリニックの受付（人物なし）",
            telop="AAFPRS 会員調査 2021：医師の77% が「自撮りでよく見せたい」動機の患者増を回答"),
        img("2021年には、77パーセントの", 3, "clinic2", "【数字】施術室の別カットに替えて77%の数値提示へ"),
        img("写真が先で、顔が後", 4, "filter2", "【決め文】「写真が先で、顔が後」。スマホのカメラで撮影する手元（S4の再掲）で保持"),
        img("ここまでが、研究で分かっていることよ", 5, "filter1", "【切り替え】自撮りする手元の別カットに替えて推論パートへの予告へ"),
    ],
    6: [
        img(None, 1, "mirror3", "【推論①の導入】鏡の前でネクタイを結ぶ後ろ姿",
            telop="推論①：美は努力や投資で手に入れてよい → 見た目を仕事の強みにする人への抵抗が弱まる"),
        img("生まれつきの顔じゃなくて", 2, "mirror1", "【問い返し】鏡の別カットに替えて「美しさを手に入れてもいい」の確認へ"),
        img("そう考える人が増えると", 3, "mirror2", "【推論①の帰結】鏡の別カットに替えて抵抗が弱まる、への接続"),
        img("もう一つは、ハロー効果よ", 4, "ringlight1", "【推論②の導入】リングライトの前で語る人（S1の再掲）",
            telop="推論②：ハロー効果 → 顔と人柄が見える一人ひとりへの偏見が弱まる → 仕事への見方も変わる"),
        img("ハロー効果が弱めるのは", 5, "ringlight3", "【限定】カメラを構える後ろ姿に替えて「まず一人ひとりへの偏見」の限定へ"),
        img("外見の価値が上がれば", 6, "ringlight2", "【接続】横顔でリングライトに取り付ける場面に替えて仕事への評価への接続へ"),
        img("冒頭の疑問が", 7, "ringlight1", "【次章への問い】S1と同じ写真に戻し「これだけで説明できるのか」へ"),
    ],
    7: [
        img(None, 1, "streamer1", "【補強する変化①の導入】配信デスク（マイク・キーボード・画面）",
            telop="補強する変化①：個人が自分の名前で発信できる → 肩書きではなく一人の人として見られる"),
        img("さっきの元キャバ嬢の人も", 2, "streamer2", "【当てはめ】無人のポッドキャストスタジオに替えてS1の当事者への接続"),
        img("そうなると、肩書きだけでなく", 3, "streamer3", "【接続】ノートPCとマイクのデスクに替えて「肩書きより一人の人」への接続"),
        img("知り合いみたい", 4, "phone1", "【知り合いみたいという感覚】スマホ画面操作の手元（S1の再掲）"),
        img("自分で決めていい", 5, "pen2", "【補強する変化②の導入】書類にサインする手元",
            telop="補強する変化②：自分の体と生き方は自分で決める（環境の批判とは両立）"),
        img("そう考える人が、以前より増えたのよ", 6, "pen1", "【合いの手】サインの別カットに替えて「外野が責めるな」の一言へ"),
        img("本人の選択を尊重することと", 7, "pen3", "【留保】サインの別カットに替えて環境批判との両立の一言へ"),
        img("SNSは、外見と、その人の物語を", 8, "pen2", "【接続】最初のサインの手元に戻し二つの変化の結びつきへ"),
        img("でも、きれいすぎて", 9, "pen1", "【次章への問い】サインの別カットに替えて「穴はないのか」の疑いへ"),
    ],
    8: [
        chapter(),
        img(None, 1, "portrait1", "【反証①の伏線】1972年はSNSより前という事実。人物写真のプリント（再掲）",
            telop="反証①：SNSは偏りを生んだのではなく、強めた"),
        img("いいところに気づいたわね", 2, "portrait2", "【確認】白黒写真の別カットに替えて「偏りを強めた」の確認へ"),
        diagram(
            "美しい人が好かれやすくなる一方で",
            "【対比: 受け入れる力／はじく力】反証②。右列（はじく力）を「一緒に強まるのよ」で出す",
            sketch(
                [
                    [
                        cell("accept", "美しい人を歓迎", icon="favorite", at="美しい人が好かれやすくなる一方で"),
                        cell("reject", "基準外は低評価", icon="thumb_down", at="はじく力が一緒に強まるのよ", after="はじく力が一緒に強まるのよ"),
                    ]
                ],
                caption={"text": "受け入れる力とはじく力が強まる", "at": "はじく力が一緒に強まるのよ"},
            ),
        ),
        img("三つ目は", 3, "clinic1", "【反証③】整形容認と性産業容認は別問題。美容クリニック（再掲）",
            telop="反証③：整形の容認と性産業の容認は別の問題"),
        img("確かに、整形は自分の顔の話で", 4, "clinic3", "【留保】施術室の別カットに替えて「そこまでなら言える」への着地"),
        img("そこまでなら言えそうね", 5, "night1", "【締め】夜の路地のネオン（再掲）で結論へのつなぎ"),
    ],
    9: [
        diagram(
            None,
            "【converge: 結論】ずんだもんの整理に同期して4要因が「偏見が弱まる」へ収束する（構造が主張）",
            {
                "type": "narrative",
                "layout": "converge",
                "items": [
                    {"id": "halo", "text": "ハロー効果", "at": "ディオンの実験で出てきた癖なのだ"},
                    {"id": "premium", "text": "経済的プレミアム", "at": "賃金に差がつくほど価値を持っていた"},
                    {"id": "sns", "text": "写真SNS", "at": "写真SNSが来て"},
                    {"id": "self", "text": "発信と自己決定", "at": "自分のことは自分で決める考え方も重なった"},
                ],
                "result": {"text": "偏見が弱まる", "at": "見た目を仕事に生かす人への偏見が弱まったのだ"},
            },
        ),
        img("はじく力の話なのだ", 1, "scale2", "【反証②への回帰】同じ力が選別の圧力にもなる。天秤",
            telop="同じ力は、見た目で選別する圧力にもなる（採用・評価・SNSのコメント）"),
        img("同じルッキズムの力は", 2, "scale1", "【本題】天秤の別カットに替えて選別の圧力そのものの説明へ"),
        img("受け入れられた人の裏で", 3, "scale3", "【裏側】アンティークの天秤に替えて厳しく見られる人の存在へ"),
        img("私は、それがいちばん大切だと思うわ", 4, "scale2", "【一番大切なこと】最初の天秤に戻し裏側を忘れないという結び"),
        img("見た目で選ばれやすくなった社会は", 5, "closing1", "【結び】決め文と同時に夜の街の光と光るスマホを持つ手（象徴的な最後の一枚。アウトロで保持）"),
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
