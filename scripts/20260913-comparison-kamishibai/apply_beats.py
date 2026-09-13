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
  カットとして採用（mri_a）。S1の時計は薬瓶が写らない方（clock_b）。
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
    "walk": "Photo: Kassia Melo / Pexels",  # 原綴 Kássia Melo
    "phone_morning": "Photo: LinkedIn Sales Navigator / Pexels",
    "coffee": "Photo: Thirdman / Pexels",
    "stretch": "Photo: Mikhail Nilov / Pexels",
}

# 採用元ファイル（candidates-comparison/stock/{ファイル名}）→ render-assets へ配置するときの対応。
SOURCE_FILE = {
    "phone": "stock/s01_phone_a.jpg",
    "handshake": "stock/s01_handshake_a.jpg",
    "clock": "stock/s01_clock_b.jpg",
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
    "walk": "stock/s09_walk_a.jpg",
    "phone_morning": "stock/s10_phone_morning_a.jpg",
    "coffee": "stock/s10_coffee_a.jpg",
    "stretch": "stock/s10_stretch_a.jpg",
}

# 台本「発音・ポーズメモ」の読み。preflight（VOICEVOX audio_query の読み突合）で誤読が
# 確認されたものだけを登録する（正しく読む語を登録すると複合語の読みが壊れるため）。
# 2026-09-13 実測: 銀メダル・銅メダル・MRI・妬み・フェスティンガー・ギロビッチ・4.8点・
# 7.1点・17ポイント・82%・40%・13%・9%・一歩・4位・金 はいずれも VOICEVOX が正しく読む
# （audio_query で直接確認済み）ため登録しない。「銀が上」だけ「ギンガジョオ」と誤読する
# （S2・S4 の同一表現。前後の「上を見る」等は正しく「うえ」と読むため、この特定表現の
# サーフィスだけを登録する）。
GLOBAL_READINGS: list[tuple[str, str]] = [
    ("銀が上", "ギンガウエ"),
    ("五輪で行ったの", "ゴリンデオコナッタノ"),  # 「いったの」と誤読（実施した、の意）
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 台本「発音・ポーズメモ」のうち（間 N）で明示済みでないもの（生成側の既定値＝話者交代0.45・
# 文境界0.35・章末1.2 から動かす箇所だけ）。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [("やめられないのだ", 0.9)],
    7: [("封印するのだ", 0.6)],
    10: [
        ("その使い方だったの", 1.5),
        ("頑張って、ずんだもん", 0.8),
        ("3時前に眠るのだ", 2.0),
    ],
}

# 道しるべの板（S5・S6。章の頭で同じ板を出し、該当行を highlight_lines で金色にする）。
GUIDE_BOARD = "\n".join([
    "比較の、壊れた二つの前提",
    "① 誰と比べるか",
    "② 相手の何を見るか",
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
    # ---------------- S1 フック（同期の昇進を見た夜） ----------------
    1: [
        img(None, 1, "phone", "【夜のスマホ】暗い部屋でスマホを見る手元で開く（台本指定の静止画）"),
        img("同期の昇進報告", 2, "handshake", "【昇進報告】スーツ姿の握手カットに替え、流れてきた投稿を示す"),
        img("3時まで眠れなかった", 3, "clock", "【異常事態】ベッドサイドの時計に替え、無音でも伝わるようテロップを添える",
            telop="3時まで眠れなかった"),
        img("今日は、その理由を一緒に確かめましょう", 4, "clock", "【保持の分割】同じ時計カットを保持したまま20秒超を避けるための継続カット"),
        img("壊れているのよ", 5, "clock", "【保持の分割】同じ時計カットを保持したまま20秒超を避けるための継続カット（2）"),
        img("道具みたいなものね", 6, "clock", "【保持の分割】同じ時計カットを保持したまま20秒超を避けるための継続カット（3）"),
    ],
    # ---------------- S2 「比較」とは何か、答えを先に ----------------
    2: [
        board("揃えておきましょうか", "【用語の定義】比較の定義を黒板に固定し、以後の章が参照できるようにする",
              telop="比較\n＝自分がどのくらいか\n他人を見て測ること"),
        img("仕事ができるか", 1, "office2", "【測る対象の例】オフィスで談笑する写真に替え、日常の「できる／できない」判断の例を示す"),
        img("壊れているのは二つ", 2, "office2", "【対比の予告】同じオフィス写真を保持したまま、壊れた二つの前提をテロップで出す",
            telop="壊れているのは ①誰と比べるか ②相手の何を見るか"),
        img("自分で選び直せばいいの", 3, "office2", "【保持の分割】同じオフィス写真を保持したまま20秒超を避けるための継続カット"),
        board("まず一つ目ね", "【板の進行1/3】見出し＋①だけを出す（②③はまだ）",
              telop="ひっくり返る三つの思い込み\n① 比較は悪い癖"),
        board("二つ目", "【板の進行2/3】②を書き足す",
              telop="ひっくり返る三つの思い込み\n① 比較は悪い癖\n② 上を見るから苦しい"),
        board("三つ目は", "【板の進行3/3】③を書き足して三つ揃える",
              telop="ひっくり返る三つの思い込み\n① 比較は悪い癖\n② 上を見るから苦しい\n③ みんな充実して見える"),
    ],
    # ---------------- S3 なぜ、比べずにいられないのか ----------------
    3: [
        chapter(),
        board(None, "【出典の提示】フェスティンガーの理論名だけを黒板に出して開く", telop="フェスティンガーの社会的比較（1954）"),
        board("ここが出発点よ", "【保持の分割】同じ見出しの板を保持したまま10秒超を避けるための継続ビート",
              telop="フェスティンガーの社会的比較（1954）"),
        board("それなら分かるのだ", "【保持の分割】同じ見出しの板を保持したまま10秒超を避けるための継続ビート（2）",
              telop="フェスティンガーの社会的比較（1954）"),
        img("身長や体重なら", 1, "scale", "【測れるものの例】体重計に乗る足元に替え、目盛りがある例を示す"),
        board("目盛りがないとき、人は", "【板の進行2/3】①（目盛りがないときは他人で測る）を書き足す",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る"),
        board("近い人を選びやすいの", "【板の進行3/3】②（近い人を選ぶ）を書き足す",
              telop="フェスティンガーの社会的比較（1954）\n① 目盛りがない→他人で測る\n② 相手は、近い人を選ぶ"),
        img("落ち込むのは、同期よ", 2, "office3", "【近い相手の例】同年代の同僚が並ぶオフィスに替え、同期という近い相手の例を示す"),
        img("ほかに使える目盛りがない", 3, "office3", "【保持の分割】同じオフィス写真を保持したまま決め文の位置で継続カット"),
        img("ドイツのボン大学などの研究チームが", 4, "office3",
            "【研究の出典】同じオフィス写真を保持したまま、実施機関と年をテロップで出す",
            telop="ボン大学など 33人（2007）",
            source="Festinger, L. (1954). A theory of social comparison processes. Human Relations, 7(2), 117–140."),
        img("一人ずつ入ってもらった", 4, "mri", "【実験装置】検査装置の写真に替え、MRIに入ってもらう場面を示す",
            source="Fliessbach, K. et al. (2007). Science, 318(5854), 1305–1308."),
        diagram(
            "隣の人がもらった額も見せられる",
            "【実験の構造】自分の額は同じでも、相手の額の多寡で脳の反応が上下する格子を見せる",
            sketch(
                [
                    [
                        cell("own1", icon="payments", text="自分の額 同じ", at="隣の人がもらった額も見せられる", after="隣の人がもらった額も見せられる"),
                        cell("other1", icon="person", text="相手の額 少ない", at="隣の人がもらった額も見せられる", after="隣の人がもらった額も見せられる"),
                        cell("react1", icon="trending_up", text="脳の反応 ↑", at="反応が下がったの", after="反応が下がったの"),
                    ],
                    [
                        cell("own2", icon="payments", text="自分の額 同じ", at="隣の人がもらった額も見せられる", after="隣の人がもらった額も見せられる"),
                        cell("other2", icon="person", text="相手の額 多い", at="隣の人がもらった額も見せられる", after="隣の人がもらった額も見せられる"),
                        cell("react2", icon="trending_down", text="脳の反応 ↓", at="反応が下がったの", after="反応が下がったの"),
                    ],
                ],
            ),
        ),
    ],
    # ---------------- S4 上を見るから、苦しいのか ----------------
    4: [
        chapter(),
        img(None, 1, "podium", "【表彰台】チャプター背景として無人の表彰台で開く"),
        img("バルセロナ五輪で行ったの", 2, "podium",
            "【研究の出典】同じ表彰台写真を保持したまま、コーネル大学の研究だとテロップで示す",
            telop="コーネル大学 1992年バルセロナ五輪の映像（1995）",
            source="Medvec, V. H., Madey, S. F., & Gilovich, T. (1995). When less is more. Journal of Personality and Social Psychology, 69(4), 603–610."),
        img("この人はどのくらい幸せそうか", 3, "podium", "【保持の分割】同じ表彰台写真を保持したまま採点方法を示す位置で継続カット"),
        diagram(
            "銅メダリストの平均は7.1点",
            "【逆転の構造】銅メダリストの方が高得点という一対の数字と、それぞれが見上げ／見下ろす先（金／4位）を格子で見せる",
            sketch(
                [
                    [cell("gold", text="金", at="銀メダリストが見ていたのは、金", after="銀メダリストが見ていたのは、金"), None],
                    [
                        cell("silver", text="銀メダリスト", value="4.8", at="銀メダリストは、4.8点よ", after="4.8点よ"),
                        cell("bronze", text="銅メダリスト", value="7.1", at="銅メダリストの平均は7.1点", after="7.1点"),
                    ],
                    [None, cell("fourth", text="4位", at="4位を見て", after="4位を見て")],
                ],
                arrows=[("silver", "gold"), ("bronze", "fourth")],
                caption={"text": "10点満点・競技直後", "at": "銅メダリストの平均は7.1点", "after": "7.1点"},
            ),
        ),
    ],
    # ---------------- S5 相手の、何が見えているのか ----------------
    5: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出し、この章が②相手の何を見るかの話だと示す",
              telop=GUIDE_BOARD, highlight_lines=[3]),
        img("落ち込んだことを、人に隠したか", 1, "classroom", "【調査の場面】明るい教室の学生たちに替え、大学生への質問調査を示す",
            telop="スタンフォード大学 大学生80人（2011）",
            source="Jordan, A. H., Monin, B., Dweck, C. S., Lovett, B. J., John, O. P., & Gross, J. J. (2011). Misery has more company than people think. Personality and Social Psychology Bulletin, 37(1), 120–135."),
        img("落ち込んだ出来事の40％は隠されていたわ", 2, "classroom",
            "【隠された割合】同じ教室写真を保持したまま、40%/13%の従テロップを出す",
            telop="落ち込みは40％隠す／うれしさは13％"),
        diagram(
            "別の学生80人に",
            "【予想の外れ方】学生80人に→予想させた→実際より17ポイント低かった、を横一列で見せる",
            sketch(
                [
                    [
                        cell("subj", icon="group", text="学生80人に", at="別の学生80人に", after="別の学生80人に"),
                        cell("op", icon="psychology", text="落ち込んだ割合を予想", at="予想してもらったの", after="予想してもらったの"),
                        cell("result", icon="trending_down", value="17pt", text="低く予想された", at="17ポイントも低かった", after="17ポイントも低かった"),
                    ],
                ],
                arrows=[("subj", "op"), ("op", "result")],
            ),
        ),
        img("落ち込んだ夜までは見えない", 3, "window5", "【見えない夜】夜の窓辺の後ろ姿に替え、見えない落ち込みを象徴させる"),
        img("3時まで眠れない夜があったかもしれない", 4, "window5", "【保持の分割】同じ窓辺写真を保持したまま継続カット"),
        img("SNS が生まれる前からあった", 5, "window5", "【保持の分割】同じ窓辺写真を保持したまま継続カット（2）"),
    ],
    # ---------------- S6 SNS は相手を選ばせない（S5の続き・章カードなし） ----------------
    6: [
        board(None, "【道しるべ】章カードは無いが冒頭に板を出す（①誰と比べるか）",
              telop=GUIDE_BOARD, highlight_lines=[2]),
        img("パーティーによく行くか", 1, "party", "【調査の場面】賑やかなパーティー写真に替え、300人への質問調査を示す",
            telop="コーネル大学 300人（2017）",
            source="Deri, S., Davidai, S., & Gilovich, T. (2017). Home alone. Journal of Personality and Social Psychology, 113(6), 858–877."),
        img("82％が", 2, "party", "【意外な数字】同じパーティー写真を保持したまま、82%の回答をテロップで出す",
            telop="82％ が『他人の方がパーティーに行く』と回答"),
        img("他人より少ないなんて、変なのだ", 3, "party", "【保持の分割】同じパーティー写真を保持したまま継続カット"),
        img("家で本を読んでいる人", 4, "reading6", "【浮かばない例】家で読書する写真に替え、思い浮かばない側の生活を示す"),
        img("ここから先は、研究じゃなくて私の推論ね", 5, "reading6", "【保持の分割】同じ読書写真を保持したまま継続カット"),
        img("何百人分も流れてくる", 6, "scroll", "【SNSの偏り】スクロールする手元に替え、偏った瞬間が大量に流れてくる様子を示す"),
        img("僕が相手を選ぶ前に、相手の方から流れてくるのだ", 7, "scroll", "【保持の分割】同じスクロール写真を保持したまま継続カット"),
        img("それも、一番いい瞬間ばかりがよ", 8, "scroll", "【保持の分割】同じスクロール写真を保持したまま継続カット（2）"),
        img("推論と言ったのは", 9, "scroll", "【保持の分割】同じスクロール写真を保持したまま継続カット（3）"),
    ],
    # ---------------- S7 眺めるだけで、気分は落ちるのか ----------------
    7: [
        chapter(),
        img(None, 1, "laptop", "【実験の準備】明るい部屋でノートPCに向かう学生で開く"),
        img("10分間、Facebook を使ってもらう", 2, "laptop",
            "【研究の出典】同じ写真を保持したまま、実施機関と年をテロップで出す",
            telop="ミシガン大学など 学生67人（2015）",
            source="Verduyn, P. et al. (2015). Passive Facebook usage undermines affective well-being. Journal of Experimental Psychology: General, 144(2), 480–488."),
        img("その日の夜", 3, "glow7", "【時間差】暗い部屋でスマホの光に照らされた顔に替え、夜になって出る変化を示す"),
        diagram(
            "眺めた組だけ",
            "【因果の鎖】眺めるだけ→妬み→夜の気分が下がる、を1本の鎖で見せる。動く組の変化なしはcaptionで補う",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "watch", "text": "眺めるだけ", "icon": "visibility", "at": "眺めた組だけ", "after": "眺めた組だけ"},
                    {"id": "envy", "text": "妬み", "icon": "mood_bad", "at": "妬みよ", "after": "妬みよ"},
                    {"id": "mood_down", "text": "夜の気分↓9%", "icon": "trending_down", "at": "眺める、妬む、気分が下がる、の順ね", "after": "気分が下がる"},
                ],
                "caption": {"text": "動く組は変化なし", "at": "動いた組には変化がなかったの", "after": "動いた組には変化がなかった"},
            },
        ),
    ],
    # ---------------- S8 「やめればいい」への答え（反証の章・章カードなし） ----------------
    8: [
        img(None, 1, "phonedesk", "【勢いを受ける】机に伏せて置かれたスマホで開く"),
        img("アカウントを止めてもらった", 2, "phonedesk", "【研究の出典】同じ写真を保持したまま、実施機関と年をテロップで出す",
            telop="スタンフォード大学・ニューヨーク大学（2020）",
            source="Allcott, H., Braghieri, L., Eichmeyer, S., & Gentzkow, M. (2020). The welfare effects of social media. American Economic Review, 110(3), 629–676."),
        img("8割の人が", 3, "phonedesk", "【結果】同じ写真を保持したまま、幸福感の変化をテロップで出す",
            telop="4週間で幸福感が上がった／8割『止めてよかった』"),
        img("1日30分に制限", 4, "timer", "【別の実験】タイマーの写真に替え、ペンシルベニア大学の制限実験を示す",
            telop="ペンシルベニア大学 学生143人（2018）",
            source="Hunt, M. G., Marx, R., Lipson, C., & Young, J. (2018). No more FOMO. Journal of Social and Clinical Psychology, 37(10), 751–768."),
        img("孤独感が減ったわ", 5, "timer", "【結果】同じタイマー写真を保持したまま、孤独感減少をテロップで出す",
            telop="1日30分制限・3週間: 孤独感が減少"),
        diagram(
            "残る偏りがあるわ",
            "【半分だけ正解】SNSをやめる→少し楽になる、比べる癖→残る、の対比を格子で見せる"
            "（台本の逐語アンカー「止めてよかった」「残るのだ」は写真ビートと交差するため、"
            "図解1本にまとめて後段で出す形に調整）",
            sketch(
                [
                    [
                        cell("snsstop", icon="phonelink_erase", text="SNSをやめる", at="僕の頭の中の同期は消えない", after="僕の頭の中の同期は消えない"),
                        cell("relief", icon="sentiment_satisfied", text="少し楽になる", at="僕の頭の中の同期は消えない", after="僕の頭の中の同期は消えない"),
                    ],
                    [
                        cell("bias", icon="visibility_off", text="比べる癖", at="僕の頭の中の同期は消えない", after="僕の頭の中の同期は消えない"),
                        cell("remain", icon="repeat", text="残る", at="僕の頭の中の同期は消えない", after="僕の頭の中の同期は消えない"),
                    ],
                ],
                arrows=[("snsstop", "relief"), ("bias", "remain")],
            ),
        ),
        img("目標にもなるのよ", 6, "running", "【良い面】ランナーの後ろ姿に替え、比べることの良い面（目標）を示す"),
    ],
    # ---------------- S9 どう、使い直すのか ----------------
    9: [
        chapter(),
        board(None, "【板の進行1/4】見出しだけを出す", telop="比べ方の使い直し"),
        board("最初の二つは", "【保持の分割】同じ見出しの板を保持したまま10秒超を避けるための継続ビート",
              telop="比べ方の使い直し"),
        board("一つ目", "【板の進行2/4】①（見えない部分も数に入れる）を書き足す",
              telop="比べ方の使い直し\n① 見えない部分も数に入れる"),
        board("二つ目", "【板の進行3/4】②（話しかける）を書き足す",
              telop="比べ方の使い直し\n① 見えない部分も数に入れる\n② 話しかける"),
        img("話しかけること", 1, "cafe9", "【話しかける例】カフェで向かい合って話す写真に替え、二つ目の使い直しを示す"),
        img("相手の見える範囲が広がるかもしれないわ", 2, "cafe9", "【保持の分割】同じカフェ写真を保持したまま継続カット"),
        board("三つ目。", "【板の進行4/4】③（比べる相手を自分で決める）を書き足して三つ揃える",
              telop="比べ方の使い直し\n① 見えない部分も数に入れる\n② 話しかける\n③ 比べる相手を自分で決める"),
        img("比べる相手を、自分で決めること", 2, "walk", "【相手を選ぶ例】友人数人の後ろ姿に替え、三つ目の使い直しを示す"),
        img("感覚が消えたの", 4, "walk", "【結果】同じ写真を保持したまま、結果をテロップで出す",
            telop="比べる相手を変えると、『自分の方が劣っている』感覚が消えた",
            source="Deri, S., Davidai, S., & Gilovich, T. (2017). Study 6A. コーネル大学 154人"),
        img("この実験は社交生活の話だから", 5, "walk", "【保持の分割】同じ写真を保持したまま継続カット"),
        diagram(
            "銀と銅で、何を見たかによって",
            "【S4の再掲】銀と銅の対比図解をまとめて一度に再掲し、何を基準にしたかで見え方が変わることを思い出させる",
            sketch(
                [
                    [cell("gold2", text="金", at="銀と銅で、何を見たかによって", after="銀と銅で、何を見たかによって"), None],
                    [
                        cell("silver2", text="銀メダリスト", value="4.8", at="銀と銅で、何を見たかによって", after="銀と銅で、何を見たかによって"),
                        cell("bronze2", text="銅メダリスト", value="7.1", at="銀と銅で、何を見たかによって", after="銀と銅で、何を見たかによって"),
                    ],
                    [None, cell("fourth2", text="4位", at="銀と銅で、何を見たかによって", after="銀と銅で、何を見たかによって")],
                ],
                arrows=[("silver2", "gold2"), ("bronze2", "fourth2")],
            ),
        ),
    ],
    # ---------------- S10 結び（冒頭の夜に戻る） ----------------
    10: [
        img("昨日の夜まで、戻ってみましょうか", 1, "phone_morning", "【朝に戻る】S1と同じスマホの手元だが朝の光で開く"),
        img("見えている一枚の裏を", 2, "coffee", "【裏を見に行く】二人でコーヒーを飲む写真に替え、見える一枚の裏を見に行く様子を示す"),
        img("比べること自体は", 3, "stretch", "【象徴的な最後の一枚】朝の窓辺で伸びをする人で終え、アウトロへつなぐ"),
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
