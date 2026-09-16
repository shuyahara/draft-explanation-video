"""めたん×ずんだもん版「人はなぜ他人と比べてしまうのか」（Issue #38・10シーン）: ビート
（貼り写真 / 章カード / 黒板文字 / チョーク図解）と readings・pause_after を YAML に貼り直す。

  .venv\\Scripts\\python.exe scripts/20260913-comparison-kamishibai/apply_beats.py

冒頭で台本 md から YAML（narration 部）を **毎回生成し直す**（台本は推敲で動くため、
手で生成コマンドを打つのを忘れて古い narration にビートを貼る事故を防ぐ）。生成は

  python tools/kamishibai_md_to_yaml.py <台本md> --v5-yaml <同フォルダの empty-v5-stub.yaml>
      --out <同名yaml> --bgm ../bgm/aozora-ni-kuchibue.mp3
      --bgm-credit "BGM:「青空に口笛」のる（DOVA-SYNDROME）" --puppet-sink 0.12 --tempo 1.1

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（v7・淫夢版などと同じ方式）。

貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-comparison/scene_NN_beat{slot}.*`
（配置は stage_assets.py）。

---------------------------------------------------------------------------
設計メモ（2026-09-13。台本 v3 に対応）
---------------------------------------------------------------------------
■ 道しるべの板（S5・S6）
  「比較の、壊れた二つの前提／①誰と比べるか／②相手の何を見るか」を両シーンの頭（from=1）で
  出し、S5 は②（3行目）、S6 は①（2行目）を highlight_lines で金色にする（見出しが1行目）。

■ 板の進行表示（板2・板3・板4）
  台本の「①②③を順に出す」指示は、board ビートが telop 全体を静的に表示する仕様のため
  （diagram のような要素単位の累積表示は無い）、**同じ板を複数の board ビートに分けて
  見出し→+①→+①②→+①②③ と段階的に差し替える**ことで近似した（各 board ビートの
  cut_reason に明記）。

■ 図解 5 箇所（台本指定どおりの型）
  S3 sketch(2行3列+矢印) → S4 sketch(3行2列+矢印) → S5 sketch(1行3列) →
  S7 narrative chain → S8 sketch(2行2列+矢印)

■ 写真と図解/板は同時に出せない（紙芝居モードは図解ビートで背景を敷かない）
  台本の「写真の切り替え」と「図解要素の出現」が同じ区間内で入れ子になっている箇所は、
  ビートの逐次性に合わせて並べ替えた（**ナレーションは1文字も変えていない**。ラベル・
  演出タイミングのみの調整）。
  - S7（図4）: 「その日の夜」の写真切り替えを図解の直前に前出しし、図解（眺める→妬み→
    気分が下がる）は写真が切り替わった後にまとめて出す。下段「動く組は変化なし」は
    chain 型が並行2系統を持てないため caption で表現した。
  - S8（図5）: 台本の「止めてよかった」「残るのだ」アンカーは v3 改稿で「残るのだ」の
    文言が消えたため、意味の対応する新アンカー「僕の頭の中の同期は消えないのだ」に
    差し替えた（帰結は同じ＝比べる癖は残る）。上段・下段とも短い間隔でまとめて出す
    （台本の逐語アンカーへ写真を割り込ませると図解の範囲が分断されるため）。

■ ツール制約で詰めたところ（**ナレーションは1文字も変えていない。板・図解のラベルのみ**）
  - board の telop は複数行で最大4行。長い定義文・思い込みリストは見出し＋要約行に詰めた
    （例: S2 板1「比較／＝自分がどのくらいか／他人を見て測ること」）。
  - sketch のセル text は12文字上限のため、「自分がもらう額」→「自分の額」のように詰めた。
  - S9 末尾（「銀と銅で、何を見たかによって」以降）は台本が「S4の図2再掲」を許可しているため、
    一枚絵の保持が20秒を超えないよう実際に再掲図解（サマリー版）を挿入した。

■ 章カード 5 枚（S3・S4・S5・S7・S9。台本どおり）／道しるべ板 2 回（S5・S6）

■ 貼り写真の採用（候補は 素材メモ.md・2026-09-13 コーディネーター指示）
  各アンカーは素材メモの「推奨」候補を採用。見つからなかった3箇所の判断:
  S4表彰台=無人の表彰台（podium_a）、S8タイマー=タイマー単独（timer_b。stopwatch画面）、
  S8ランニング=後ろ姿単独（running_c）。S3のMRI写真はCTの可能性があるが汎用の検査装置
  カットとして採用（mri_a）。S1の時計は clock_b（4:12）がテロップ「3時まで眠れなかった」と
  食い違うため、2026-09-13 に clock_c（3:33表示）へ差し替え（Issue #38）。
"""
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
REPO = HERE.parents[1]
YAML_PATH = HERE / "20260913-comparison-kamishibai.yaml"
MD_PATH = HERE / "20260913-comparison-kamishibai.md"

# 出典表記（貼り写真の下＝字幕帯の右下）。素材メモ.md の候補一覧から転記（ASCII 化した箇所は
# 原綴を併記。matome 版と同じ理由でダイアクリティカル記号は黒板フォントで□になる）。
CREDIT = {
    "phone": "Photo: Jaroslav Maler / Pexels",  # 原綴 Maléř
    "handshake": "Photo: Khwanchai Phanthong / Pexels",
    "clock": "Photo: cottonbro studio / Pexels",
    "office2": "Photo: Yan Krukau / Pexels",
    "scale": "Photo: Annushka Ahuja / Pexels",
    "office3": "Photo: Mikhail Nilov / Pexels",
    "mri": "Photo: Pexels",  # v8 で mri_gen に差し替え（実は CT 装置でロゴが読めた）
    "mri_gen": "Image: AI generated",
    "podium": "Photo: Szcze hoo / Pexels",  # v8 で podium_gen に差し替え（無人で表情が見せられない）
    "podium_gen": "Image: AI generated",
    "classroom": "Photo: RDNE Stock project / Pexels",
    "window5": "Photo: cottonbro studio / Pexels",
    "party": "Photo: Pavel Danilyuk / Pexels",
    "reading6": "Photo: Monstera Production / Pexels",
    "scroll": "Photo: kaboompics / Pexels",
    "laptop": "Photo: kaboompics / Pexels",
    "glow7": "Photo: SHVETS production / Pexels",
    "phonedesk": "Photo: John (Giannis) Tekeridis / Pexels",
    "timer": "Photo: Image Hunter / Pexels",
    "running": "Photo: MART PRODUCTION / Pexels",  # v8 で running_gen に差し替え（追う相手が写っていない）
    "running_gen": "Image: AI generated",
    "cafe9": "Photo: RDNE Stock project / Pexels",
    "walk": "Photo: Kassia Melo / Pexels",  # 原綴 Kássia Melo（未採用。恋愛相手選びに見えるとの指摘で不採用）
    "walk2": "Photo: Keira Burton / Pexels",
    "phone_morning": "Photo: LinkedIn Sales Navigator / Pexels",
    "coffee": "Photo: Thirdman / Pexels",
    "stretch": "Photo: Mikhail Nilov / Pexels",
}

# 採用元ファイル（candidates-comparison/stock/{ファイル名}）→ render-assets へ配置するときの対応。
SOURCE_FILE = {
    "phone": "stock/s01_phone_a.jpg",
    "handshake": "stock/s01_handshake_a.jpg",
    "clock": "stock/s01_clock_c.jpg",
    "office2": "stock/s02_office_b.jpg",
    "scale": "stock/s03_scale_a.jpg",
    "office3": "stock/s03_office_a.jpg",
    "mri": "stock/s03_mri_a.jpg",
    "mri_gen": "gen/s02_mri_gen.jpg",
    "podium": "stock/s04_podium_a.jpg",
    "podium_gen": "gen/s03_podium_gen.jpg",
    "classroom": "stock/s05_classroom_a.jpg",
    "window5": "stock/s05_window_a.jpg",
    "party": "stock/s06_party_a.jpg",
    "reading6": "stock/s06_reading_a.jpg",
    "scroll": "stock/s06_scroll_a.jpg",
    "laptop": "stock/s07_laptop_a.jpg",
    "glow7": "stock/s07_glow_a.jpg",
    "phonedesk": "stock/s08_phonedesk_a.jpg",
    "timer": "stock/s08_timer_b.jpg",
    "running": "stock/s08_running_c.jpg",
    "running_gen": "gen/s07_running_gen.jpg",
    "cafe9": "stock/s09_cafe_a.jpg",
    "walk": "stock/s09_walk_a.jpg",  # 未採用（下記参照）
    "walk2": "stock/s09_walk_c.jpg",
    "phone_morning": "stock/s10_phone_morning_a.jpg",
    "coffee": "stock/s10_coffee_a.jpg",
    "stretch": "stock/s10_stretch_a.jpg",
}

# 台本「発音・ポーズメモ」の読み。preflight（VOICEVOX audio_query の読み突合）で誤読が
# 確認されたものだけを登録する（正しく読む語を登録すると複合語の読みが壊れるため）。
# 2026-09-13 実測（v4）: 170センチ・皆勤賞・MRI・妬み・フェスティンガー・ギロビッチ・4.8点・
# 7.1点・17ポイント・82%・9% はいずれも VOICEVOX が正しく読む（audio_query で直接確認済み）
# ため登録しない。「二組」は「ニクミ」と誤読するため登録。「Aさん」は「エイサン」
# （A=エイ）と読むため、台本指定の「エーさん」に登録（2026-09-15 v7・audio_query で確認）。
# 「上なのに」（S3「銀メダルの方が上なのに」）は「ジョオナノニ」と誤読するため登録
# （2026-09-16 v7 再確認・priority 10 で audio_query 実測。旧登録「銀が上」「銀の方が上」は
# v7 のセリフ変更で本文に一致しなくなったため置き換え）。
GLOBAL_READINGS: list[tuple[str, str]] = [
    ("上なのに", "ウエナノニ"),
    ("二組", "フタクミ"),
    ("Aさん", "エーサン"),
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 台本「発音・ポーズメモ」のうち（間 N）で明示済みでないもの（生成側の既定値＝話者交代0.45・
# 文境界0.35・章末1.2 から動かす箇所だけ）。2026-09-13 v4 書き直しに合わせて全面更新。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [
        ("やめられないのだ", 0.9),
        ("本能的に比較してしまうのよ", 0.8),
        ("解説していきましょうか", 0.6),
    ],
    2: [("難しいのよ", 1.5)],
    6: [("封印するのだ", 0.6)],
    7: [
        ("少し楽になるわ", 0.8),
        ("思ったよりずっと効いた", 0.9),
    ],
    8: [("予想と逆なのだ", 0.6)],
    9: [
        ("頑張って、ずんだもん", 0.8),
        ("早く眠るのだ", 2.0),
    ],
}

# 道しるべの板（S4・S5。章の頭で同じ板を出し、該当行を highlight_lines で金色にする）。
# 2026-09-15 v6: 文言変更（選び方／どこを見ているか、から、勝手に流れてくる／いいところしか
# 見えない、に統一）。
GUIDE_BOARD = "\n".join([
    "比較の、おかしくなっている二つ",
    "① 相手が勝手に流れてくる",
    "② いいところしか見えない",
])


def img(anchor, slot, credit_key, why, telop=None, source=None):
    return ("image", anchor, slot, credit_key, why, telop, source, None)


def board(anchor, why, telop=None, highlight_lines=None):
    return ("board", anchor, None, None, why, telop, None, highlight_lines)


def chapter():
    return ("chapter", None, None, None, "【章の入口】黒板に問いを書いて本題へ", None, None, None)


def diagram(anchor, why, spec):
    return ("diagram", anchor, None, None, why, spec, None, None)


def cell(id, text=None, icon=None, value=None, at=None, after=None):
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
    # ---------------- S1 フック（人と比較してしまうずんだもん。2026-09-15 v7: 台詞全面改稿） ----------------
    1: [
        img(None, 1, "phone", "【夜のスマホ】暗い部屋でスマホを見る手元で開く（台本指定の静止画）"),
        img("送ったのだ", 2, "handshake", "【昇進報告】スーツ姿の握手カットに替え、流れてきた投稿を示す"
            "（「同期の昇進報告」がcue1内に同居するため、congratulationsを送る自然な継続点へ後ろ倒し）"),
        img("なかなか眠れなかった", 3, "clock", "【異常事態】眠れない人の寝室に替え、無音でも伝わるようテロップを添える",
            telop="なかなか眠れなかった"),
        img("本能的に比較してしまうのよ", 4, "office3", "【比較の定義】同年代の同僚が並ぶオフィス（S2用候補を流用）に替え、比較の定義をテロップで出す",
            telop="比較＝自分がどのくらいかを、他人を見て測ること"),
    ],
    # ---------------- S2 なぜ、比べずにいられないのか ----------------
    2: [
        chapter(),
        img("突然だけど、身長なら", 1, "scale", "【測れるものの例】体重計に乗る足元で開く",
            source="Festinger, L. (1954). A theory of social comparison processes. Human Relations, 7(2), 117–140."),
        img("身長には数値にできる目盛りがあるわ", 2, "scale", "【保持の分割】同じ体重計の写真を保持したまま20秒超を避けるための継続カット"),
        img("他人を目盛りにするのだ", 3, "scale", "【保持の分割】同じ体重計の写真を保持したまま20秒超を避けるための継続カット（2）"),
        board("1954年に", "【板の進行1/3】見出し＋①（目盛りがない→他人で測る）を出す",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る"),
        board("欲求があるの", "【板の進行2/3】②（自分を評価したい欲求）を書き足す",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る\n② 自分を評価したい欲求"),
        board("近い人を選びやすいの", "【板の進行3/3】③（近い人を選ぶ）を書き足して三つ揃える",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る\n② 自分を評価したい欲求\n③ 相手は、近い人を選ぶ"),
        img("近い立場の知人や同僚よ", 2, "office3", "【近い相手の例】同年代の同僚が並ぶオフィスに替え、近い相手の例を示す"),
        img("脳の反応にも出るのよ", 3, "mri_gen", "【実験装置】MRI 2 台に参加者が 2 人入る生成画像に替え、二人同時に測る実験の場面へ（v8: CT 写真から差し替え）"),
        img("それをドイツのボン大学などの研究チームが", 4, "mri_gen",
            "【研究の出典】同じMRI写真を保持したまま、実施機関と年をテロップで出す",
            telop="ボン大学など 33人（2007）",
            source="Fliessbach, K. et al. (2007). Science, 318(5854), 1305–1308."),
        diagram(
            "隣の人がもらった額も見せられるわ",
            "【実験の構造】自分の額は同じでも、相手の額の多寡で脳の反応が上下する格子を見せる。"
            "決め文「難しいのよ」（間）まで保持する",
            sketch(
                [
                    [
                        cell("own1", icon="payments", text="自分の額 同じ", at="隣の人がもらった額も見せられるわ", after="隣の人がもらった額も見せられるわ"),
                        cell("other1", icon="person", text="相手の額 少ない", at="隣の人がもらった額も見せられるわ", after="隣の人がもらった額も見せられるわ"),
                        cell("react1", icon="trending_up", text="脳の反応 ↑", at="反応が下がったの", after="反応が下がったの"),
                    ],
                    [
                        cell("own2", icon="payments", text="自分の額 同じ", at="隣の人がもらった額も見せられるわ", after="隣の人がもらった額も見せられるわ"),
                        cell("other2", icon="person", text="相手の額 多い", at="隣の人がもらった額も見せられるわ", after="隣の人がもらった額も見せられるわ"),
                        cell("react2", icon="trending_down", text="脳の反応 ↓", at="反応が下がったの", after="反応が下がったの"),
                    ],
                ],
                highlight={"ids": ["react2"], "at": "反応が下がったの", "after": "反応が下がったの"},  # 決め要素だけ金色
            ),
        ),
        img("ただ、フェスティンガーも", 5, "scale", "【決め文の保持後】体重計の写真に戻し、フェスティンガー自身の限定条件を添えてシーン末まで"),
    ],
    # ---------------- S3 順位がよければ、楽になるのか ----------------
    3: [
        chapter(),
        img(None, 1, "podium_gen", "【表彰台】3 人のメダリスト（2 位だけ暗い顔で 1 位を見上げる）の生成画像で開く（v8: 無人の表彰台から差し替え）"),
        img("順位がよくても", 2, "podium_gen", "【保持の分割】同じ表彰台の写真を保持したまま20秒超を避けるための継続カット"),
        img("コーネル大学のギロビッチ教授たちが", 3, "podium_gen", "【保持の分割】同じ表彰台の写真を保持したまま20秒超を避けるための継続カット（2）"),
        diagram(
            "銅メダリストの平均は7.1点",
            "【逆転の構造】銅メダリストの方が高得点という一対の数字と、それぞれが見上げ／見下ろす先（金／4位）を格子で見せる。"
            "決め文「状況が決めていたのよ」（間）まで保持する",
            sketch(
                [
                    [cell("gold", text="金", at="2位の人は、1位を見ているの", after="2位の人は、1位を見ているの"), None],
                    [
                        cell("silver", text="銀メダリスト", value="4.8", at="銀メダリストは、4.8点だったわ", after="4.8点だったわ"),
                        cell("bronze", text="銅メダリスト", value="7.1", at="銅メダリストの平均は7.1点", after="7.1点"),
                    ],
                    [None, cell("fourth", text="4位", at="4位を見て", after="4位を見て")],
                ],
                arrows=[("silver", "gold"), ("bronze", "fourth")],
                highlight={"ids": ["bronze"], "at": "銅メダリストの平均は7.1点", "after": "7.1点"},  # 逆転した側だけ金色
                caption={"text": "10点満点・競技直後", "at": "銅メダリストの平均は7.1点", "after": "7.1点"},
            ),
        ),
        img("もっとも、本人に聞いたわけじゃないわ", 2, "podium_gen", "【保持の分割】表彰台の写真に戻し、研究の限定を言う"),
        img("テストで80点でも", 3, "classroom", "【S4用写真を流用】教室の学生の写真に替え、身近な例（テストの点数）からシーン末へ"),
    ],
    # ---------------- S4 相手の、何が見えているのか ----------------
    4: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出し、この章が②相手のどこを見ているかの話だと示す",
              telop=GUIDE_BOARD, highlight_lines=[3]),
        board("つらいことや落ち込んだことがあったはずよ", "【保持の分割】同じ板を保持したまま20秒超を避けるための継続ビート",
              telop=GUIDE_BOARD, highlight_lines=[3]),
        img("スタンフォード大学の研究チームが", 1, "classroom", "【調査の場面】明るい教室で話す学生たちに替え、大学生への質問調査を示す",
            source="Jordan, A. H., Monin, B., Dweck, C. S., Lovett, B. J., John, O. P., & Gross, J. J. (2011). Misery has more company than people think. Personality and Social Psychology Bulletin, 37(1), 120–135."),
        img("落ち込んだ出来事の40％は", 2, "classroom",
            "【隠された割合】同じ教室写真を保持したまま、40%/13%の従テロップを出す",
            telop="落ち込みは 40％ 隠す ／ うれしさは 13％",
            source="スタンフォード大学 大学生80人（2011）"),
        diagram(
            "別の学生80人に",
            "【予想の外れ方】学生80人に→予想させた→実際より17ポイント低かった、を横一列で見せる",
            sketch(
                [
                    [
                        cell("subj", icon="group", text="学生80人に", at="別の学生80人に", after="別の学生80人に"),
                        cell("op", icon="psychology", text="落ち込んだ割合を予想", at="予想してもらったのよ", after="予想してもらったのよ"),
                        cell("result", icon="trending_down", value="17pt", text="低く予想された", at="17ポイントも低かったわ", after="17ポイントも低かったわ"),
                    ],
                ],
                arrows=[("subj", "op"), ("op", "result")],
                highlight={"ids": ["result"], "at": "17ポイントも低かったわ", "after": "17ポイントも低かったわ"},  # 主役の数字だけ金色
            ),
        ),
        img("その人が落ち込んだ夜までは", 3, "window5", "【見えない夜】夜の窓辺の後ろ姿に替え、見えない落ち込みを象徴させる"),
        img("同期にも、なかなか眠れない夜があったかもしれない", 4, "window5", "【保持の分割】同じ窓辺写真を保持したまま20秒超を避けるための継続カット"),
        img("SNSが登場する前の", 4, "classroom", "【教室へ戻る】SNSより前の状況だったと限定する位置で教室の写真に戻し、シーン末まで保持"),
    ],
    # ---------------- S5 SNS は相手を選ばせない（S4の続き・章カードなし） ----------------
    5: [
        img(None, 1, "party", "【開幕の受け】まだ板は出さず、賑やかなパーティー写真の気配だけで開く"),
        board("比べる相手まで勝手に決まってしまうのよ", "【道しるべ】冒頭の受けの直後に板を出す（①比べる相手の選び方）",
              telop=GUIDE_BOARD, highlight_lines=[2]),
        img("パーティーによく行く人", 2, "party", "【調査の場面】賑やかなパーティー写真に替え、300人への質問調査を示す"),
        img("そんなずんだもんに", 3, "party", "【保持の分割】同じパーティー写真を保持したまま20秒超を避けるための継続カット"),
        diagram(
            "300人に聞いたの",
            "【調査の構造】300人に→自分と他人どちらが多く行くか→82%が『他人』、を横一列で見せる（v8: 写真＋テロップの数字だけだった箇所。"
            "Deri, Davidai & Gilovich 2017, JPSP 113(6)）。「友人の数を聞いても」で写真に戻す",
            sketch(
                [
                    [
                        cell("deri_n", icon="group", text="300人に聞いた", at="300人に聞いたの", after="300人に聞いたの"),
                        cell("deri_q", icon="psychology", text="どちらが多く行くか", at="どちらがパーティーによく行くと思うか", after="よく行くと思うか"),
                    ],
                    [
                        None,
                        cell("deri_r", icon="trending_up", value="82%", text="『他人の方が多い』", at="82％が", after="82％が"),
                    ],
                ],  # 2 段（S4 の 1x3 格子と同じ形が続く警告を避ける）
                arrows=[("deri_n", "deri_q"), ("deri_q", "deri_r")],
                highlight={"ids": ["deri_r"], "at": "82％が", "after": "82％が"},
                caption={"text": "ギロビッチ教授ら（2017）", "at": "300人に聞いたの", "after": "300人に聞いたの"},
            ),
        ),
        img("友人の数を聞いても", 4, "party", "【写真に戻す】図解のあとパーティー写真に戻し、他の質問でも同じだったと言う"),
        img("家でゆっくりしているような人は", 4, "reading6", "【浮かばない例】家で読書する写真に替え、思い浮かばない側の生活を示す"),
        img("そしてSNSは、この偏りを", 5, "scroll", "【SNSの偏り】スクロールする手元に替え、偏った瞬間が大量に流れてくる様子を示す"),
        img("それが何百人分も流れてくるの", 6, "scroll", "【保持の分割】同じスクロール写真を保持したまま20秒超を避けるための継続カット"),
        img("しかも、いいところだけね", 7, "scroll", "【保持の分割】同じスクロール写真を保持したまま20秒超を避けるための継続カット（2）"),
        img("僕、相手も選べてないし", 6, "party", "【パーティーへ戻る】まとめの位置でパーティー写真に戻し、章末の問いへ渡す"),
    ],
    # ---------------- S6 眺めるだけで、気分は落ちるのか ----------------
    6: [
        chapter(),
        img(None, 1, "laptop", "【実験の準備】明るい部屋でノートPCに向かう学生で開く"),
        img("10分間、Facebookを使ってもらったのよ", 2, "laptop",
            "【研究の出典】同じ写真を保持したまま、実施機関と年をテロップで出す",
            telop="ミシガン大学など 学生67人（2015）",
            source="Verduyn, P. et al. (2015). Passive Facebook usage undermines affective well-being. Journal of Experimental Psychology: General, 144(2), 480–488."),
        img("その日の夜に測ったの", 3, "phone", "【時間差】S1冒頭と同じ夜のスマホの手元（顔なし）に替え、夜になって出る変化を示す"),
        img("眺めた組だけ", 4, "phone", "【結果】同じ夜のスマホの手元を保持したまま、9%低下／変化なしをテロップで出す",
            telop="眺める組: 夜の気分 約9％低下／動く組: 変化なし"),
        img("眺めただけなのに", 5, "phone", "【保持の分割】同じ夜のスマホの手元を保持したまま20秒超を避けるための継続カット"),
        img("実験の外でも調べているわ", 6, "phone", "【保持の分割】同じ夜のスマホの手元を保持したまま20秒超を避けるための継続カット（2）"),
        img("僕、気分が悪いから見続けてたと思ってたのだ", 7, "phone", "【保持の分割】同じ夜のスマホの手元を保持したまま20秒超を避けるための継続カット（3）"),
        diagram(
            "眺めたあとに妬みが生まれて",
            "【因果の鎖】眺めるだけ→妬み→夜の気分が下がる、を1本の鎖で見せる。三要素は同一キューへ語同期。"
            "決め文「落ちなかったのよ」（間）まで保持する",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "watch", "text": "眺めるだけ", "icon": "visibility", "at": "眺めたあとに妬みが生まれて", "after": "眺めた"},
                    {"id": "envy", "text": "妬み", "icon": "mood_bad", "at": "眺めたあとに妬みが生まれて", "after": "妬みが生まれて"},
                    {"id": "mood_down", "text": "夜の気分↓9%", "icon": "trending_down", "at": "眺めたあとに妬みが生まれて", "after": "気分が下がっていた"},  # chain 型は強調色を持たない（仕様）
                ],
                "caption": {"text": "動く組は変化なし", "at": "自分から動いた組は", "after": "自分から動いた組は"},
            },
        ),
        img("僕のも、たぶんそれなのだ", 5, "laptop", "【落ち着いて限定】明るい部屋のノートPCの写真に戻し、シーン末まで保持"
            "（画面指定の旧アンカー「下がったのは気分だけで」は台詞削除で消失したため、後続の最も近い節目に前出し）"),
    ],
    # ---------------- S7 「やめればいい」への答え（反証の章・章カードなし） ----------------
    7: [
        img(None, 1, "phonedesk", "【勢いを受ける】机に伏せて置かれたスマホで開く"),
        img("スタンフォード大学とニューヨーク大学の経済学者たちが", 2, "phonedesk",
            "【研究の出典】同じ写真を保持したまま、実施機関と年をテロップで出す",
            telop="スタンフォード大学・ニューヨーク大学（2020）",
            source="Allcott, H., Braghieri, L., Eichmeyer, S., & Gentzkow, M. (2020). The welfare effects of social media. American Economic Review, 110(3), 629–676."),
        diagram(
            "Facebookの利用者をランダムに二組に分けて",
            "【実験の構造】上段: 利用者を2組に→片方だけ4週間停止→幸福感が少し上昇（Allcott et al. 2020, AER 110(3)）。"
            "下段: 学生143人→1日30分に制限→孤独感が減少（Hunt et al. 2018, JSCP 37(10)）。学生の引用文まで保持する"
            "（v8: 写真＋テロップだけだった 2 研究を図解に）",
            sketch(
                [
                    [
                        cell("fb_n", icon="group", text="利用者を2組に", at="Facebookの利用者をランダムに二組に分けて", after="二組に分けて"),
                        cell("fb_op", icon="phonelink_erase", text="片方だけ4週間停止", at="Facebookの利用者をランダムに二組に分けて", after="止めてもらったの"),
                        cell("fb_r", icon="trending_up", text="幸福感が少し上昇", at="止めた組は、幸福感が少し上がったわ", after="少し上がったわ"),
                    ],
                    [
                        cell("pa_n", icon="school", text="学生143人", at="ペンシルベニア大学でも", after="ペンシルベニア大学でも"),
                        cell("pa_op", icon="timer", text="1日30分に制限", at="ペンシルベニア大学でも", after="3週間続けてもらったの"),
                        cell("pa_r", icon="trending_down", text="孤独感が減少", at="こっちは孤独感が減ったわ", after="孤独感が減ったわ"),
                    ],
                ],
                arrows=[("fb_n", "fb_op"), ("fb_op", "fb_r"), ("pa_n", "pa_op"), ("pa_op", "pa_r")],
                highlight={"ids": ["fb_r", "pa_r"], "at": "こっちは孤独感が減ったわ", "after": "孤独感が減ったわ"},
                caption={"text": "8割が『止めてよかった』", "at": "8割の人が", "after": "8割の人が"},
            ),
        ),
        img("参加した学生の一人は", 3, "phonedesk", "【引用文】図解を 30 秒弱で閉じ、机のスマホに戻して学生の言葉を聞かせる"),
        board("ちょっと待って", "【板の進行1/2】見出し＋①（減らせば少し楽になる）を出す（v8: 台詞の写しだった格子図解を板に替え、前の図解との連続を避ける）",
              telop="SNSをやめれば解決か\n① 減らせば、少し楽になる"),
        board("消えないのだ", "【板の進行2/2】②（頭の中の比較は止まらない）を書き足して金色に。決め文「止まらないのよ」（間）まで保持する",
              telop="SNSをやめれば解決か\n① 減らせば、少し楽になる\n② 頭の中の比較は、止まらない", highlight_lines=[3]),
        img("良い面もあるの", 6, "running_gen", "【良い面】前を走る人を追うランナーの生成画像に替え、比べることの良い面（目標）を示す（v8: 単独の後ろ姿から差し替え）"),
        img("手が届きそうな相手なら", 7, "running_gen", "【保持の分割】同じランナーの写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S8 どうすればいいのか（2026-09-16 v7: 電車の実験を外しLiu 2023単独に） ----------------
    8: [
        chapter(),
        img(None, 1, "timer", "【タイマー開幕】資格の合否・走ったタイムの喩えを先取りしてタイマー写真で開く（章の背景も兼ねる）"),
        board("趣味とかを一つ持てばいいのよ", "【板の進行1/2】見出し＋①（目盛りのあるものを持つ）を出す",
              telop="比べ方の使い直し\n① 目盛りのあるものを持つ"),
        img("資格の合否、走ったタイム", 2, "timer", "【具体例】同じタイマー写真を保持したまま、目盛りのある例を示す"),
        img("そこでは他人を見る必要がないから", 3, "timer", "【保持の分割】同じタイマー写真を保持したまま20秒超を避けるための継続カット"),
        board("それから、SNSは眺めるだけで終えないこと", "【板の進行2/2】②（その人に話しかける）を書き足す",
              telop="比べ方の使い直し\n① 目盛りのあるものを持つ\n② 眺めるだけで終えず、その人に話しかける"),
        img("気になった相手がいたら", 3, "phone", "【夜のスマホへ】S1と同じ夜のスマホの手元に替え、気まずさの話に入る"),
        img("でも、昇進した相手に話しかけるのは", 4, "phone", "【保持の分割】同じ夜のスマホ写真を保持したまま20秒超を避けるための継続カット"),
        img("実際に一言メッセージを送ってもらったの", 5, "phone_morning", "【朝のスマホへ】S9用の朝のスマホの手元を流用し、Liu 2023の実験へ切り替える"),
        diagram(
            "送った側は",
            "【予想と実際】送った側の予想 5.57 点 → 相手の実際 6.17 点（7 点満点・54 組）を 2 セルで並べ、予想の方が低かったことを見せる。"
            "「予想と逆なのだ」まで保持する（v8: 写真＋テロップだけだった箇所。Liu, Rim, Min & Min 2023, JPSP 124(4), Experiment 2）",
            sketch(
                [
                    [
                        cell("liu_pred", icon="mood", value="5.57点", text="送った側の予想", at="送った側は", after="予想していたけど"),
                        cell("liu_real", icon="sentiment_very_satisfied", value="6.17点", text="相手の実際の喜び", at="送った側は", after="予想より喜んでいたわ"),
                    ],
                ],
                arrows=[("liu_pred", "liu_real")],
                highlight={"ids": ["liu_real"], "at": "送った側は", "after": "予想より喜んでいたわ"},
                caption={"text": "7点満点・54組（2023）", "at": "送った側は", "after": "予想していたけど"},
            ),
        ),
        img("メッセージでもいいし、会う約束をして", 6, "cafe9", "【会って聞く】カフェで向かい合って話す写真に替え、会って聞く提案を示す"),
        img("自分から動いた組は気分が下がらなかったし", 7, "cafe9", "【保持の分割】同じカフェ写真を保持したまま、動いた組の出典を示す",
            source="Verduyn, P. et al. (2015). Passive Facebook usage undermines affective well-being. Journal of Experimental Psychology: General, 144(2), 480–488."),
        img("SNSをやめてしまってもいいし", 8, "cafe9", "【保持の分割】同じカフェ写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S9 結び（なぜ比べてしまうのか。2026-09-15 v6: 全面改稿） ----------------
    9: [
        board(None, "【板の進行1/4】見出しだけを出す（cue1はめたんの問いかけと同居するため、見出しのみ短く保持）",
              telop="なぜ他人と比べてしまうのか"),
        board("他人で測るしかないのだ", "【板の進行2/4】①（目盛りがない→他人で測る）を書き足す",
              telop="なぜ他人と比べてしまうのか\n① 目盛りがない→他人で測る"),
        board("脳もその差に反応する", "【板の進行3/4】②（脳は差に反応する）を書き足す",
              telop="なぜ他人と比べてしまうのか\n① 目盛りがない→他人で測る\n② 脳は差に反応する"),
        board("見えないからよ", "【板の進行4/4】③（相手は流れてきて、いいところしか見えない）を書き足して三つ揃える。決め文（間2.0）まで保持",
              telop="なぜ他人と比べてしまうのか\n① 目盛りがない→他人で測る\n② 脳は差に反応する\n③ 相手は流れてきて、いいところしか見えない"),
        img("昨日の夜の続きだけど", 1, "phone_morning", "【朝に戻る】S1と同じスマホの手元だが朝の光で開く"),
        img("会って聞くのだ", 2, "coffee", "【会って聞く】二人でコーヒーを飲む写真に替え、会って聞く様子を示す"),
        img("それなら、今夜は眠れそうね", 3, "stretch", "【象徴的な最後の一枚】朝の窓辺で伸びをする人で終え、アウトロへつなぐ"),
    ],
}


def regenerate_yaml() -> None:
    cmd = [
        sys.executable,
        str(REPO / "tools" / "kamishibai_md_to_yaml.py"),
        str(MD_PATH),
        "--v5-yaml", str(HERE / "empty-v5-stub.yaml"),
        "--out", str(YAML_PATH),
        "--bgm", "../bgm/aozora-ni-kuchibue.mp3",
        "--bgm-credit", "BGM:「青空に口笛」のる（DOVA-SYNDROME）",
        "--puppet-sink", "0.12",
        "--tempo", "1.1",
    ]
    subprocess.run(cmd, check=True, cwd=str(REPO))


def cues_of(scene) -> list[str]:
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
    regenerate_yaml()
    doc = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    total = 0
    for scene in doc["scenes"]:
        sid = scene["id"]
        cues = cues_of(scene)
        beats = []
        last_from = 0
        img_i = 0
        for kind, anchor, slot, ckey, why, telop, source, highlight_lines in BEATS[sid]:
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
                b["slot"] = img_i
                b["credit"] = f"{source}／{CREDIT[ckey]}" if source else CREDIT[ckey]
            if kind == "diagram":
                b["diagram"] = resolve_ats(telop, cues, sid)
            elif telop:
                b["telop"] = telop
            if kind == "board" and highlight_lines:
                b["highlight_lines"] = list(highlight_lines)
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
