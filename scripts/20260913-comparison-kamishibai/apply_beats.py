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
    "mri": "Photo: Pexels",
    "podium": "Photo: Szcze hoo / Pexels",
    "classroom": "Photo: RDNE Stock project / Pexels",
    "window5": "Photo: cottonbro studio / Pexels",
    "party": "Photo: Pavel Danilyuk / Pexels",
    "reading6": "Photo: Monstera Production / Pexels",
    "scroll": "Photo: kaboompics / Pexels",
    "laptop": "Photo: kaboompics / Pexels",
    "glow7": "Photo: SHVETS production / Pexels",
    "phonedesk": "Photo: John (Giannis) Tekeridis / Pexels",
    "timer": "Photo: Image Hunter / Pexels",
    "running": "Photo: MART PRODUCTION / Pexels",
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
    "podium": "stock/s04_podium_a.jpg",
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
# ため登録しない。「上」がらみの語（銀が上・銀の方が上）は「ジョオ」と誤読するため個別登録。
# 「二組」も「ニクミ」と誤読するため登録。「Aさん」は「エイサン」（A=エイ）と読むため、
# 台本指定の「エーさん」に登録（2026-09-15 v7・audio_query で確認）。
GLOBAL_READINGS: list[tuple[str, str]] = [
    ("銀が上", "ギンガウエ"),
    ("銀の方が上", "ギンノホウガウエ"),
    ("二組", "フタクミ"),
    ("Aさん", "エーサン"),
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 台本「発音・ポーズメモ」のうち（間 N）で明示済みでないもの（生成側の既定値＝話者交代0.45・
# 文境界0.35・章末1.2 から動かす箇所だけ）。2026-09-13 v4 書き直しに合わせて全面更新。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [
        ("やめられないのだ", 0.9),
        ("他人を見ることしかないからよ", 0.8),
    ],
    2: [("難しいのよ", 1.5)],
    6: [("封印するのだ", 0.6)],
    7: [
        ("少し楽になるわ", 0.8),
        ("思ったよりずっと効いた", 0.9),
    ],
    9: [
        ("頑張って、ずんだもん", 0.8),
        ("3時前に眠るのだ", 2.0),
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
    # ---------------- S1 フック（同期の昇進を見た夜。2026-09-15 v5: 旧S1+旧S2を統合） ----------------
    1: [
        img(None, 1, "phone", "【夜のスマホ】暗い部屋でスマホを見る手元で開く（台本指定の静止画）"),
        img("送ったのだ", 2, "handshake", "【昇進報告】スーツ姿の握手カットに替え、流れてきた投稿を示す"
            "（「同期の昇進報告」がcue1内に同居するため、congratulationsを送る自然な継続点へ後ろ倒し）"),
        img("3時まで眠れなかった", 3, "clock", "【異常事態】3時台を示す時計に替え、無音でも伝わるようテロップを添える",
            telop="3時まで眠れなかった"),
        img("性格が悪いからじゃないの", 4, "office3", "【目盛りのない例】同年代の同僚が並ぶオフィス（S2用候補を流用）に替え、比較の理由説明に入る"),
        img("他人を見ることしかないからよ", 5, "office3", "【比較の定義】同じオフィス写真を保持したまま、比較の定義をテロップで出す",
            telop="比較＝自分がどのくらいかを、他人を見て測ること"),
        img("見えていないの", 6, "office3", "【予告】同じオフィス写真を保持したまま、おかしくなっている二つをテロップで出す",
            telop="おかしくなっているのは ①相手が流れてくる ②いいところだけ"),
    ],
    # ---------------- S2 なぜ、比べずにいられないのか ----------------
    2: [
        chapter(),
        img("身長なら、目盛りがあるわ", 1, "scale", "【測れるものの例】体重計に乗る足元で開く",
            source="Festinger, L. (1954). A theory of social comparison processes. Human Relations, 7(2), 117–140."),
        img("だから、他人を目盛りにするのだ", 2, "scale", "【保持の分割】同じ体重計の写真を保持したまま20秒超を避けるための継続カット"),
        board("1954年に", "【板の進行1/3】見出し＋①（目盛りがない→他人で測る）を出す",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る"),
        board("欲求があるの", "【板の進行2/3】②（自分を評価したい欲求）を書き足す",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る\n② 自分を評価したい欲求"),
        board("近い人を選びやすいの", "【板の進行3/3】③（近い人を選ぶ）を書き足して三つ揃える",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る\n② 自分を評価したい欲求\n③ 相手は、近い人を選ぶ"),
        img("落ち込むのは、同期よ", 2, "office3", "【近い相手の例】同年代の同僚が並ぶオフィスに替え、同期という近い相手の例を示す"),
        img("脳の反応にも出るのよ", 3, "mri", "【実験装置】検査装置の写真に替え、MRIに入ってもらう場面へ"),
        img("それをドイツのボン大学などの研究チームが", 4, "mri",
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
            ),
        ),
        img("ただ、フェスティンガーも", 5, "scale", "【決め文の保持後】体重計の写真に戻し、フェスティンガー自身の限定条件を添えてシーン末まで"),
    ],
    # ---------------- S3 順位がよければ、楽になるのか ----------------
    3: [
        chapter(),
        img(None, 1, "podium", "【表彰台】チャプター背景として無人の表彰台で開く"),
        img("順位がよくても", 2, "podium", "【保持の分割】同じ表彰台の写真を保持したまま20秒超を避けるための継続カット"),
        img("コーネル大学のギロビッチ教授たちが", 3, "podium", "【保持の分割】同じ表彰台の写真を保持したまま20秒超を避けるための継続カット（2）"),
        diagram(
            "銅メダリストの平均は7.1点",
            "【逆転の構造】銅メダリストの方が高得点という一対の数字と、それぞれが見上げ／見下ろす先（金／4位）を格子で見せる。"
            "決め文「状況が決めていたのよ」（間）まで保持する",
            sketch(
                [
                    [cell("gold", text="金", at="銀の人は、金を見ているの", after="銀の人は、金を見ているの"), None],
                    [
                        cell("silver", text="銀メダリスト", value="4.8", at="銀メダリストは、4.8点だったわ", after="4.8点だったわ"),
                        cell("bronze", text="銅メダリスト", value="7.1", at="銅メダリストの平均は7.1点", after="7.1点"),
                    ],
                    [None, cell("fourth", text="4位", at="4位を見て", after="4位を見て")],
                ],
                arrows=[("silver", "gold"), ("bronze", "fourth")],
                caption={"text": "10点満点・競技直後", "at": "銅メダリストの平均は7.1点", "after": "7.1点"},
            ),
        ),
        img("もっとも、本人に聞いたわけじゃないわ", 2, "podium", "【保持の分割】表彰台の写真に戻し、研究の限定を言う"),
        img("テストで80点でも", 3, "classroom", "【S4用写真を流用】教室の学生の写真に替え、身近な例（テストの点数）からシーン末へ"),
    ],
    # ---------------- S4 相手の、何が見えているのか ----------------
    4: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出し、この章が②相手のどこを見ているかの話だと示す",
              telop=GUIDE_BOARD, highlight_lines=[3]),
        board("同期にもつらい夜があったとして", "【保持の分割】同じ板を保持したまま20秒超を避けるための継続ビート",
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
            ),
        ),
        img("その人が落ち込んだ夜までは", 3, "window5", "【見えない夜】夜の窓辺の後ろ姿に替え、見えない落ち込みを象徴させる"),
        img("同期にも、3時まで眠れない夜があったかもしれない", 4, "window5", "【保持の分割】同じ窓辺写真を保持したまま20秒超を避けるための継続カット"),
        img("対面の大学生活を調べたものよ", 4, "classroom", "【教室へ戻る】SNSは関係ないと限定する位置で教室の写真に戻し、シーン末まで保持"),
    ],
    # ---------------- S5 SNS は相手を選ばせない（S4の続き・章カードなし） ----------------
    5: [
        img(None, 1, "party", "【開幕の受け】まだ板は出さず、賑やかなパーティー写真の気配だけで開く"),
        board("比べる相手まで勝手に決まってしまうのよ", "【道しるべ】冒頭の受けの直後に板を出す（①比べる相手の選び方）",
              telop=GUIDE_BOARD, highlight_lines=[2]),
        img("パーティーによく行く人", 2, "party", "【調査の場面】賑やかなパーティー写真に替え、300人への質問調査を示す"),
        img("皆勤賞のずんだもんに", 3, "party", "【保持の分割】同じパーティー写真を保持したまま20秒超を避けるための継続カット"),
        img("82％が", 3, "party", "【意外な数字】同じパーティー写真を保持したまま、82%の回答をテロップで出す",
            telop="82％ が『他人の方がパーティーに行く』と回答",
            source="Deri, S., Davidai, S., & Gilovich, T. (2017). Home alone. Journal of Personality and Social Psychology, 113(6), 858–877."),
        img("友人の数でも、外食の回数でも", 4, "party", "【保持の分割】同じパーティー写真を保持したまま20秒超を避けるための継続カット（2）"),
        img("家で本を読んでいる人は", 4, "reading6", "【浮かばない例】家で読書する写真に替え、思い浮かばない側の生活を示す"),
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
                    {"id": "mood_down", "text": "夜の気分↓9%", "icon": "trending_down", "at": "眺めたあとに妬みが生まれて", "after": "気分が下がっていた"},
                ],
                "caption": {"text": "動く組は変化なし", "at": "自分から動いた組は", "after": "自分から動いた組は"},
            },
        ),
        img("下がったのは気分だけで", 5, "laptop", "【落ち着いて限定】明るい部屋のノートPCの写真に戻し、限定条件を言ってシーン末まで"),
        img("でも僕には、その気分こそが問題なのだ", 6, "laptop", "【保持の分割】同じノートPCの写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S7 「やめればいい」への答え（反証の章・章カードなし） ----------------
    7: [
        img("勢いがいいわね", 1, "phonedesk", "【勢いを受ける】机に伏せて置かれたスマホで開く"),
        img("スタンフォード大学とニューヨーク大学の経済学者たちが", 2, "phonedesk",
            "【研究の出典】同じ写真を保持したまま、実施機関と年をテロップで出す",
            telop="スタンフォード大学・ニューヨーク大学（2020）",
            source="Allcott, H., Braghieri, L., Eichmeyer, S., & Gentzkow, M. (2020). The welfare effects of social media. American Economic Review, 110(3), 629–676."),
        img("止めた組は、幸福感が少し上がったわ", 3, "phonedesk", "【保持の分割】同じスマホ写真を保持したまま20秒超を避けるための継続カット"),
        img("8割の人が", 3, "phonedesk", "【結果】同じ写真を保持したまま、幸福感の変化をテロップで出す",
            telop="4週間で幸福感が上がった／8割『止めてよかった』"),
        img("ペンシルベニア大学でも", 4, "timer", "【別の実験】タイマーの写真に替え、ペンシルベニア大学の制限実験を示す",
            source="Hunt, M. G., Marx, R., Lipson, C., & Young, J. (2018). No more FOMO. Journal of Social and Clinical Psychology, 37(10), 751–768."),
        img("こっちは孤独感が減ったわ", 5, "timer", "【結果】同じタイマー写真を保持したまま、孤独感減少をテロップで出す",
            telop="1日30分制限・3週間: 孤独感が減少", source="ペンシルベニア大学 学生143人（2018）"),
        diagram(
            "ちょっと待って",
            "【半分だけ正解】SNSをやめる→少し楽になる、頭の中で比べる癖→残る、の対比を格子で見せる。"
            "決め文「止まらないのよ」（間）まで保持する",
            sketch(
                [
                    [
                        cell("snsstop", icon="phonelink_erase", text="SNSをやめる", at="ちょっと待って", after="ちょっと待って"),
                        cell("relief", icon="sentiment_satisfied", text="少し楽になる", at="ちょっと待って", after="ちょっと待って"),
                    ],
                    [
                        cell("bias", icon="visibility_off", text="比べる癖", at="消えないのだ", after="消えないのだ"),
                        cell("remain", icon="repeat", text="残る", at="消えないのだ", after="消えないのだ"),
                    ],
                ],
                arrows=[("snsstop", "relief"), ("bias", "remain")],
            ),
        ),
        img("良い面もあるの", 6, "running", "【良い面】ランナーの後ろ姿に替え、比べることの良い面（目標）を示す"),
        img("手が届きそうな相手なら", 7, "running", "【保持の分割】同じランナーの写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S8 じゃあ、どうすればいいのか（2026-09-15 v6: 全面改稿） ----------------
    8: [
        chapter(),
        img(None, 1, "timer", "【タイマー開幕】資格の合否・走ったタイムの喩えを先取りしてタイマー写真で開く（章の背景も兼ねる）"),
        board("目盛りのあるものを一つ持てばいいのよ", "【板の進行1/2】見出し＋①（目盛りのあるものを持つ）を出す",
              telop="比べ方の使い直し\n① 目盛りのあるものを持つ"),
        img("資格の合否、走ったタイム", 2, "timer", "【具体例】同じタイマー写真を保持したまま、目盛りのある例を示す"),
        img("そこでは他人を見る必要がないから", 3, "timer", "【保持の分割】同じタイマー写真を保持したまま20秒超を避けるための継続カット"),
        board("それから、SNSは眺めるだけで終えないこと", "【板の進行2/2】②（一人に絞って聞く）を書き足す",
              telop="比べ方の使い直し\n① 目盛りのあるものを持つ\n② 眺めるだけで終えず、一人に絞って聞く"),
        img("落ち込んだら、いま誰と比べているのか", 3, "phone", "【夜のスマホへ】S1と同じ夜のスマホの手元に替え、一人だけ名指しする話に入る"),
        img("劣等感が消えたの", 4, "phone", "【結果】同じ写真を保持したまま、劣等感が消えた結果をテロップで出す",
            telop="思い浮かべる相手を特定の知人に指定→劣等感が消えた",
            source="Deri, S., Davidai, S., & Gilovich, T. (2017). Study 6A. コーネル大学154人（2017）"),
        img("でも、昇進した相手に聞くのは", 5, "phone", "【保持の分割】同じ夜のスマホ写真を保持したまま20秒超を避けるための継続カット"),
        img("メッセージでもいいし、会う約束をして", 5, "cafe9", "【会って聞く】カフェで向かい合って話す写真に替え、会って聞く提案を示す"),
        img("自分から動いた組は気分が下がらなかったし", 6, "cafe9", "【保持の分割】同じカフェ写真を保持したまま、動いた組の出典を示す",
            source="Verduyn, P. et al. (2015). Passive Facebook usage undermines affective well-being. Journal of Experimental Psychology: General, 144(2), 480–488."),
        img("SNSをやめてしまってもいいし", 7, "cafe9", "【保持の分割】同じカフェ写真を保持したまま20秒超を避けるための継続カット"),
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
