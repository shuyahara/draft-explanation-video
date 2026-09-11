"""めたん×ずんだもん版・「なぜ"まとも"な男性はモテないのか」**v4（9シーン）**: ビート
（貼り写真 / 章カード / 黒板文字 / チョーク図解）と追加 readings・pause_after を YAML に貼り直す。

  .venv\\Scripts\\python.exe scripts/20260911-matome-dansei-kamishibai/apply_beats.py

冒頭で台本 md から YAML（narration 部）を **毎回生成し直す**（台本は推敲で動くため、
手で生成コマンドを打つのを忘れて古い narration にビートを貼る事故を防ぐ）。生成は

  python tools/kamishibai_md_to_yaml.py <台本md> --v5-yaml <同フォルダの empty-v5-stub.yaml>
      --out <同名yaml> --bgm ../bgm/meisou-no-piano.mp3
      --bgm-credit "BGM:「瞑想のピアノ」lei（DOVA-SYNDROME）" --puppet-sink 0.12 --tempo 1.1

`--tempo 1.1` は台本ヘッダの「話者交代 0.45・文境界 0.35（--tempo 1.1）」に合わせている
（既定の 1.0 だと話者交代 0.40・章末 1.0 になり、台本の指定とずれる）。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（v3・淫夢版・男女論版と同じ方式）。

貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-matome/scene_NN_beat{slot}.*`
（配置は stage_assets.py）。

---------------------------------------------------------------------------
v4 の設計メモ（2026-09-11。v3=14シーン から 9シーン へ全面改稿）
---------------------------------------------------------------------------
■ 道しるべの板（全編の骨格）
  S2 で「三つの段階」を黒板に書き、以後 **各章の頭で同じ板を 5 秒ほど出し、該当する段階の
  行末に「← いまここ」を付ける**（S3=①会う前 / S4=②会ったあと / S5=② / S6=② / S7=③続いてから /
  S8=①）。章カードのある章（S3・S5・S6・S7・S8）は章カードの直後、S4 は章カードが無いので
  シーン冒頭のキュー1 に置く。S9 は別の板「段階ごとの答え」を 1 行ずつ足す（3 枚）。

  板の尺: `board` ビートは次のビートまでが尺になるので、章頭の板は本文の最初の 1〜2 キューを
  覆う位置に次の image ビートを置いて 5〜8 秒に収めている（preflight の複数行ボード上限 20 秒）。

  S2 の板だけは 2 回に分けている。台本「演出」欄が主軸の二文（「段階ごとに違うの」
  「判断が終わってしまう」）を板のまま言う指定で、三つの段階の提示（キュー19〜22）から
  主軸の二文（キュー25〜28）まで通しで板にすると約 33 秒になり、複数行ボードの上限
  20 秒を超えるため。間に ずんだもん の受け（キュー23〜24）を写真 1 枚はさんでいる。

■ 図解 7 箇所（台本の指定どおりの型。隣接する図解で同じ layout を使っていない）
  S2 radiate → S3 sketch → S4 chart → S5 sketch → S6 chain → S7 sketch → S8 converge
  sketch は 3 回（S3・S5・S7）だが隣接しない。格子の形も
  S3=2行3列の流れ図 / S5=2列×3行の対比 / S7=2行3列の分岐 と変えてある。

■ ツール側の制約で台本の字面から詰めたところ（**ナレーションは 1 文字も変えていない**）
  - `narrative` のラベルは 12 文字まで（`NARRATIVE_LABEL_MAX_LENGTH`）。S6 chain の 3 段は
    台本の字面（「子育ての負担が、男女で違う」「負担が重い側が選び、軽い側が競う」
    「選ぶ側は、見て分かる手がかりで判断する（健康・力・一目置かれているか）」）が 13〜35 字
    あるため、**語を残して読点・括弧・重複語だけを落とし**
    「子育ての負担が男女で違う」(12) /「重い側が選び軽い側が競う」(12) /
    「見て分かる手がかりで選ぶ」(12) にした。caption は台本どおり。
  - `chart` の値ラベルは小数1桁に丸められる（`_format_chart_value`）。S4 は 0.43/0.29/0.19 が
    0.4/0.3/0.2 と出てしまうため、項目ラベル側に値を入れた（台本の「ラベルに値を含める。
    ツールの丸め表示との二重表示は許容」の指定どおり）。label は 8 文字以内。
  - `sketch` は行3・列4・セル12 が上限、セル本文は 12 文字まで。S5 の「左列に四つ」は 4 行
    必要なので「犯罪・浮気をしない」「働いている・優しい」の 2 セルに畳んだ（語は台本のまま）。
  - 1行 telop（image ビート）は自動縮小されないので 30 字以内に収め、**研究の出典（著者・年・
    誌名）は `credit`（字幕帯右下の小文字）へ**回した（`img(..., source=...)`）。
  - ビート境界はキュー境界にしか置けないので、同一キュー内の対比（S5 の「開いた姿勢 →
    縮こまった姿勢」）は次のキュー（ずんだもんの「姿勢だけで！？」）で切り替えている。

■ 図解の `at`（S6 chain だけ台本の指定と違う）
  台本は「決め文『ずれているのは、そこよ』の 1〜2 秒前に 3 段目が出る」としているが、その決め文は
  chain の中身（親の投資→選ぶ側/競う側→見て分かる手がかり）を語り終えた **約 60 秒後**にあり、
  指定どおりにすると図解 1 枚で 90 秒以上持たせることになる（「列挙・収束の図解だけでシーンを
  長く持たせない」に反する）。3 段目は該当の台詞（「だから、見て分かる手がかりが使われたの」）に
  同期させ、図解の保持を約 30 秒にとどめた。**要レビュー**。

■ 貼り写真
  台本が名指ししたファイル（`s01_phone_c` `s01_cafe_a` `s02_commute_e` `s04_facetoface_b`
  `s04_facetoface_a` `s05_laughing_a` `s06_open_c` `s06_closed_a` `s07_intimidate_c`
  `s07_respect_a` `s10_checking_watch_a` `s09_meeting_room_a` `s11_1930s_wedding_b`
  `s14_group_activity_g` `s14_group_activity_f`）は指定の位置で使い、尺を分けるための前後の
  カットは同じモチーフの別候補（manifest-s01-s07 / s08-s14）から採った。
  S6 の 4 カット（石器／赤ん坊を抱く親／麦畑／街を歩く男女）と S8 の結婚式場は v4 で新規に
  取得（`manifest-s08-s14.md` の末尾「v4 追加分」に出典を記録）。
  同一ファイルは動画全体で 3 ビートまで。シーンをまたぐ再利用は意味のある回収だけ
  （夜のスマホ＝会う前 / 組んだ手＝時間のかかる誠実さ / 婚礼写真・式場＝用意されていた時間）。
  `s02_commute_d` は車両に "New York Sub..." の表示が写り都市が特定できるため採らなかった。
"""
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
REPO = HERE.parents[1]
YAML_PATH = HERE / "20260911-matome-dansei-kamishibai.yaml"
MD_PATH = HERE / "20260911-matome-dansei-kamishibai.md"

# 出典表記（貼り写真の下＝字幕帯の右下）。candidates-matome の manifest から転記。
CREDIT = {
    "phone_c": "Photo: Jaroslav Maléř / Pexels",
    "phone_b": "Photo: Mikhail Nilov / Pexels",
    "phone_a": "Photo: Phil Desforges / Pexels",
    "cafe_a": "Photo: İbrahim KARASU / Pexels",
    "cafe_c": "Photo: Şeydanur Yıldız / Pexels",
    "bbs_board": "Illustration: AI generated",
    "commute_e": "Photo: Ahmad Shakir Shamsulbadri / Pexels",
    "commute_c": "Photo: Airam Dato-on / Pexels",
    "university_b": "Photo: Pixabay",
    "university_c": "Photo: Shivam / Pexels",
    "facetoface_a": "Photo: Mike Jones / Pexels",
    "facetoface_b": "Photo: RDNE Stock project / Pexels",
    "laughing_a": "Photo: Tim Douglas / Pexels",
    "laughing_d": "Photo: Alexandr / Pexels",
    "open_a": "Photo: Kindel Media / Pexels",
    "open_b": "Photo: PNW Production / Pexels",
    "open_c": "Photo: Arina Krasnikova / Pexels",
    "closed_a": "Photo: Darina Belonogova / Pexels",
    "closed_b": "Photo: RDNE Stock project / Pexels",
    "intimidate_c": "Photo: Vlada Karpovich / Pexels",
    "intimidate_a": "Photo: Kindel Media / Pexels",
    "respect_a": "Photo: Matheus Bertelli / Pexels",
    "respect_b": "Photo: Pavel Danilyuk / Pexels",
    "cafe_window_a": "Photo: Sare / Pexels",
    "cafe_window_b": "Photo: Sare / Pexels",
    "hands_a": "Photo: RDNE Stock project / Pexels",
    "hands_c": "Photo: The masked Guy / Pexels",
    "meeting_a": "Photo: Pixabay",
    "meeting_b": "Photo: Pixabay",
    "meeting_c": "Photo: Pixabay",
    "watch_a": "Photo: Arina Krasnikova / Pexels",
    "watch_d": "Photo: Pixabay",
    "wedding_b": "Illustration: AI generated",
    "office_a": "Photo: Anna Shvets / Pexels",
    "office_b": "Photo: kaboompics.com / Pexels",
    "chairs_a": "Photo: Pixabay",
    "chairs_c": "Photo: Pixabay",
    "group_g": "Photo: Thirdman / Pexels",
    "group_f": "Photo: Nataliya Vaitkevich / Pexels",
    "group_b": "Photo: cottonbro studio / Pexels",
    # v4 で新規に取得した分（S6 の起源の章・S8 の歴史の章）
    "stone_tools_a": "Photo: Rinat Askarov / Pexels",
    "stone_tools_b": "Photo: Yena Kwon / Pexels",
    "baby_parent_a": "Photo: Han Lahandoe / Pexels",
    "baby_parent_b": "Photo: Pixabay",
    "wheat_a": "Photo: Pixabay",
    "street_couple_a": "Photo: Leticia Curvelo / Pexels",
    "street_couple_b": "Photo: Pixabay",
    "venue_a": "Photo: Steven Van Elk / Pexels",
    "venue_b": "Photo: Kimy Moto / Pexels",
}

# 採用元ファイル（candidates-matome/{相対パス}）→ render-assets へ配置するときの対応。
SOURCE_FILE = {
    "phone_c": "stock/s01_phone_c.jpg",
    "phone_b": "stock/s01_phone_b.jpg",
    "phone_a": "stock/s01_phone_a.jpg",
    "cafe_a": "stock/s01_cafe_a.jpg",
    "cafe_c": "stock/s01_cafe_c.jpg",
    "bbs_board": "illust/ill_bulletin_board.png",
    "commute_e": "stock/s02_commute_e.jpg",
    "commute_c": "stock/s02_commute_c.jpg",
    "university_b": "stock/s03_university_b.jpg",
    "university_c": "stock/s03_university_c.jpg",
    "facetoface_a": "stock/s04_facetoface_a.jpg",
    "facetoface_b": "stock/s04_facetoface_b.jpg",
    "laughing_a": "stock/s05_laughing_a.jpg",
    "laughing_d": "stock/s05_laughing_d.jpg",
    "open_a": "stock/s06_open_a.jpg",
    "open_b": "stock/s06_open_b.jpg",
    "open_c": "stock/s06_open_c.jpg",
    "closed_a": "stock/s06_closed_a.jpg",
    "closed_b": "stock/s06_closed_b.jpg",
    "intimidate_c": "stock/s07_intimidate_c.jpg",
    "intimidate_a": "stock/s07_intimidate_a.jpg",
    "respect_a": "stock/s07_respect_a.jpg",
    "respect_b": "stock/s07_respect_b.jpg",
    "cafe_window_a": "stock/s08_cafe_window_a.jpg",
    "cafe_window_b": "stock/s08_cafe_window_b.jpg",
    "hands_a": "stock/s08_hands_table_a.jpg",
    "hands_c": "stock/s08_hands_table_c.jpg",
    "meeting_a": "stock/s09_meeting_room_a.jpg",
    "meeting_b": "stock/s09_meeting_room_b.jpg",
    "meeting_c": "stock/s09_meeting_room_c.jpg",
    "watch_a": "stock/s10_checking_watch_a.jpg",
    "watch_d": "stock/s10_checking_watch_d.jpg",
    "wedding_b": "illust/s11_1930s_wedding_b.png",
    "office_a": "stock/s11_office_coworkers_a.jpg",
    "office_b": "stock/s11_office_coworkers_b.jpg",
    "chairs_a": "stock/s12_facing_chairs_a.jpg",
    "chairs_c": "stock/s12_facing_chairs_c.jpg",
    "group_g": "stock/s14_group_activity_g.jpg",
    "group_f": "stock/s14_group_activity_f.jpg",
    "group_b": "stock/s14_group_activity_b.jpg",
    "stone_tools_a": "stock/s06_stone_tools_a.jpg",
    "stone_tools_b": "stock/s06_stone_tools_b.jpg",
    "baby_parent_a": "stock/s06_baby_parent_a.jpg",
    "baby_parent_b": "stock/s06_baby_parent_b.jpg",
    "wheat_a": "stock/s06_wheat_a.jpg",
    "street_couple_a": "stock/s06_street_couple_a.jpg",
    "street_couple_b": "stock/s06_street_couple_b.jpg",
    "venue_a": "stock/s08_wedding_venue_a.jpg",
    "venue_b": "stock/s08_wedding_venue_b.jpg",
}

# 台本「発音・ポーズメモ」の読み。**登録は最小限**にする（VOICEVOX が正しく読む語を登録すると
# 複合語の読みが壊れる。memory/voicevox-user-dict-priority.md）。ここに入れていない語
# （威圧・准教授・人格・石器時代・小数点の数値など）は preflight の読み突合で確認する。
# surface に助詞は含めない（辞書の読みに書くと「ハ」と発音されてしまうため）。
GLOBAL_READINGS = [
    ("博士課程", "ハクシカテイ"),
    ("一目では", "ヒトメデハ"),
    ("人柄", "ヒトガラ"),
    ("顔がいい方", "カオガイイホウ"),
    ("感じのいい方", "カンジノイイホウ"),
    ("やり方", "ヤリカタ"),
    ("通っている", "トオッテイル"),
    ("18歳", "ジュウハッサイ"),
    ("34歳", "サンジュウヨンサイ"),
    # v4 で追加した章（S6 起源 / S8 歴史）の分
    ("親の投資", "オヤノトウシ"),
    ("選択圧", "センタクアツ"),
    ("一目置かれている", "イチモクオカレテイル"),
    ("戸主", "コシュ"),
    ("仲人", "ナコウド"),
    ("基いて", "モトヅイテ"),
    ("阪井裕一郎", "サカイユウイチロウ"),
    ("山田昌弘", "ヤマダマサヒロ"),
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 台本「発音・ポーズメモ」のうち（間 N）で明示済みでないもの（生成側の既定値＝話者交代0.45・
# 文境界0.35・章末1.2 から動かす箇所だけ）。pause_after はセグメント末尾に効くので、
# セグメント末尾の一文で照合する。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [("損をするのだ", 0.9)],
}

# 道しるべの板（S2 で提示し、以後の章頭で「← いまここ」付きで再掲する）。
STAGE_BOARD_LINES = [
    "三つの段階",
    "①会う前＝写真とプロフィール",
    "②会ったあと＝初対面〜数回",
    "③続いてから＝関係が始まった後",
]


def stage_board(here: int | None = None) -> str:
    """「三つの段階」の板。`here`（1〜3）を渡すと、その段階の行末に「← いまここ」を付ける。"""
    lines = list(STAGE_BOARD_LINES)
    if here is not None:
        lines[here] = f"{lines[here]} ← いまここ"
    return "\n".join(lines)


# S2 の板「まとも」の定義（radiate の直後に 2 キューぶん）。
DEF_BOARD = "\n".join([
    "「まとも」の定義",
    "①悪いことをしない＝減点がない",
    "②相手に誠実である＝相手に向かう",
])


# S9 の板「段階ごとの答え」（ナレーションの順＝会う前→会ったあと→続いてから に 1 行ずつ足す）。
ANSWER_BOARD_LINES = [
    "段階ごとの答え",
    "①会う前＝誠実さまでは確認できない",
    "②会ったあと＝見た目・人当たり・前に出る力",
    "③続いてから＝協調性・誠実性・感情の安定",
]


def answer_board(n: int) -> str:
    """「段階ごとの答え」の板を、見出し＋先頭 n 行ぶんで作る。"""
    return "\n".join(ANSWER_BOARD_LINES[: n + 1])


def img(anchor, slot, credit_key, why, telop=None, source=None):
    """source は研究の出典（著者・年・誌名）。写真クレジットと一緒に字幕帯右下の小文字へ出す
    （telop は30字以内に収める規約のため、出典は telop ではなく credit 側に置く）。"""
    return ("image", anchor, slot, credit_key, why, telop, source)


def board(anchor, why, telop=None):
    return ("board", anchor, None, None, why, telop, None)


def chapter():
    return ("chapter", None, None, None, "【章の入口】黒板に問いを書いて本題へ", None, None)


def diagram(anchor, why, spec):
    """チョーク図解。spec 内の `at` は文字列アンカーで書き、実行時にキュー番号へ解決する。"""
    return ("diagram", anchor, None, None, why, spec, None)


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


IPSS = "国立社会保障・人口問題研究所 第16回出生動向基本調査（2021年）"

BEATS = {
    # ---------------- S1 フック（半年でマッチ3件） ----------------
    1: [
        img(None, 1, "phone_c", "【半年の書き直し】夜の部屋でスマホを見る手元から始める（台本指定の静止画）"),
        img("それで、成立したマッチは", 2, "phone_c",
            "【数字】手元の別カットに替え、マッチ3件の数字を台詞と同時にテロップで出す",
            telop="半年でマッチ3件"),
        img("実際に会えたのは1人で", 3, "cafe_a",
            "【会ったあとで止まった1件】二人分のカップに替え、会えた1人の話へ",
            telop="会えたのは1人"),
        img("僕、変なことは書いてないし", 4, "phone_a", "【書いた内容へ戻る】プロフィールの話に戻るので手元カットへ"),
        img("掲示板には", 5, "bbs_board", "【掲示板の書き込み】「まともな男ほどモテない」を見た画面（文字は描かない）"),
        img("それを、一緒に確かめましょう", 6, "cafe_c", "【問いの言語化】カフェのカットに替え、この動画が答える問いを立てる"),
        img("先に、答えの形だけ", 7, "cafe_a", "【答えの形の予告】二人分のカップに戻し「嫌われてはいない／見えない」を予告"),
        img("嫌われてはいない", 8, "phone_c", "【間】手元に戻り、ずんだもんが違いを飲み込めないところまで尺を分ける"),
    ],
    # ---------------- S2 「まとも」の中身と、三つの段階 ----------------
    2: [
        img(None, 1, "commute_e", "【当たり前の暮らし】朝の駅のホームで「まとも」の中身をほどく前振り"),
        img("犯罪はしてないのだ", 2, "office_a",
            "【四つの列挙】働く場面に替え、ずんだもんが四つ（犯罪・浮気・仕事・優しさ）を数え上げるところまで"),
        diagram(
            "最初の二つは",
            "【四つの内訳】めたんの言い直しに合わせて四つを1つずつ黒板に出し、三つが「減点なし」・四つ目だけが相手へ向かうことを見せる",
            {
                "type": "narrative",
                "layout": "radiate",
                "center": {"icon": "person", "text": "まとも", "at": "最初の二つは"},
                "items": [
                    {"id": "crime", "text": "犯罪をしない＝減点なし", "at": "最初の二つは", "after": "最初の二つは"},
                    {"id": "affair", "text": "浮気をしない＝減点なし", "at": "最初の二つは", "after": "悪いことをしていない"},
                    {"id": "work", "text": "働いている＝減点なし", "at": "三つ目の「働いている」も", "after": "無職ではない"},
                    {"id": "kind", "text": "優しい＝相手へ", "at": "相手に向かっているのは", "after": "相手に向かっているのは"},
                ],
            },
        ),
        board("だから、この動画で言う",
              "【定義の板】四つの内訳を受けて「まとも」を二つの条件で定義し、以後の章が参照する言葉を固定する",
              telop=DEF_BOARD),
        img("そして、どちらも一目では", 3, "office_a", "【定義の性質】働く場面に戻し、二つの条件とも一目では分からないと言う"),
        img("ここからは出会いの段階から", 5, "office_b", "【段階分けの前置き】働く場面の別カットに替え、段階を分ける宣言へ"),
        board("写真とプロフィールしか見えていない",
              "【全編の骨格】三つの段階を黒板に書き、以後の章頭で参照できるようにする",
              telop=stage_board()),
        img("僕は、会う前でも", 6, "phone_a", "【当事者の位置】夜のスマホの手元に替え、会う前でも会ったあとでも止まっている受けへ"),
        board("モテる要素は、段階ごとに違うの",
              "【主軸の二文】台本「演出」の指定どおり、主軸の二文は板を保持したまま言う（間1.0→2.0）",
              telop=stage_board()),
        img("僕がモテないのは、優しさがあっても", 7, "commute_e", "【次章への問い】駅のホームに戻し、優しさがあっても意味がないのかという問いで閉じる"),
    ],
    # ---------------- S3 「優しい男は損をする」は、本当なのか（会う前） ----------------
    3: [
        chapter(),
        board(None, "【道しるべ】章頭に三つの段階の板を出し、この章が①会う前の話だと示す",
              telop=stage_board(1)),
        img("これは実験されているのよ", 1, "facetoface_b",
            "【二人の男性】カフェで向かい合う男性二人に替え、2003年の実験に入る",
            source="Urbaniak & Kilmann (2003) Sex Roles 49(9/10)"),
        diagram(
            "一人は見た目の評価が高いけれど",
            "【実験の骨格】二人の男性→女子学生に聞いた→感じがいい方が選ばれた、を格子で見せる",
            sketch(
                [
                    [
                        cell("mean_man", icon="person", text="見た目◎ 意地悪", at="一人は見た目の評価が高いけれど"),
                        cell("ask", icon="forum", text="女子学生に聞いた", at="顔がいい方なのだ"),
                        cell("chosen", icon="thumb_up", text="感じがいい方が選ばれた",
                             at="選ばれたのは、感じがいい方だったの", after="選ばれたのは"),
                    ],
                    [
                        cell("nice_man", icon="person", text="見た目△ 感じがいい", at="もう一人は見た目の評価は低いけれど"),
                        None,
                        None,
                    ],
                ],
                arrows=[("mean_man", "ask"), ("nice_man", "ask"), ("ask", "chosen")],
            ),
        ),
        img("結婚相手でも、交際相手でも", 2, "university_b", "【再現性】大学の校舎に替え、二度の実験の人数を出す",
            telop="感じがいい方が選ばれた（N=48／N=194）"),
        img("でも、見た目と態度の両方が違うのだ", 3, "university_c", "【交絡への疑問】別の校舎の絵に替え、優しさだけの力かという疑問を受ける"),
        img("この実験では、見た目の良さと", 4, "facetoface_b", "【別々に効いていた】向かい合う二人に戻し、混ざっていないという説明へ"),
        img("評価が低かったのは", 5, "laughing_d", "【決め文の保持】和やかに話す二人に替え、会う前でも負けていないという決め文と間2.0秒を持たせる"),
        img("伝わりさえすれば…", 6, "cafe_window_a", "【章末の問い】カフェの窓際に替え、自分のプロフィールは伝わっていたのかという問いへ"),
    ],
    # ---------------- S4 会ったあと、実際に効いていたのは何か（会ったあと①） ----------------
    4: [
        board(None, "【道しるべ】章カードは無いがここから段階が変わるので、冒頭に板を出す（②会ったあと）",
              telop=stage_board(2)),
        img("ノースウェスタン大学のポール", 3, "facetoface_a", "【実験へ】向かい合う男女の席に替え、スピードデートの実験に入る",
            source="Eastwick & Finkel (2008) JPSP 94(2)"),
        img("まず全員に、理想の相手に", 4, "chairs_c", "【手順と人数】会場の椅子に替え、4分ずつ9〜13人と会う手順を出す",
            telop="163人／一人4分ずつ 9〜13人と"),
        img("書いたとおりの人を", 5, "chairs_a", "【当たらなかった】会場の別カットに替え、書いた理想が当たらなかったところまで"),
        diagram(
            "惹かれた度合いと結びついていたのは",
            "【相関の大きさ】数字の開きそのものが主張なので棒グラフにする。見た目の棒がいちばん長く、人当たりが稼ぐ力より長いことを見せる",
            {
                "type": "chart",
                "chart": "bar",
                "title": "恋愛的関心との相関（女性が男性を評価。男性側も順番は同じ）",
                "source": "Eastwick & Finkel (2008) JPSP 94(2)",
                "series": [
                    {
                        "color": "accent",
                        "at": "惹かれた度合いと結びついていたのは",
                        "after": "強い順に",
                        "points": [
                            {"label": "見た目0.46", "value": 0.46},
                            {"label": "人当たり0.32", "value": 0.32},
                            {"label": "稼ぐ力0.16", "value": 0.16},
                        ],
                    }
                ],
            },
        ),
        img("ただ、この順番には", 6, "laughing_a", "【人当たりの良さ】笑いながら話す二人に替え、二番目の人当たりが稼ぐ力より上で、優しさの見える部分は効いていると言う"),
        img("そして最下位の稼ぐ力は", 6, "office_b", "【稼ぐ力＝働いている】働く場面に替え、まともの中身はこの段階でいちばん弱かったと言う"),
        img("ただし、ここで測った", 6, "laughing_d", "【言葉の限定】和やかに話す二人に替え、測ったのは話していて感じがいいという評価だけだと限定する"),
        img("「優しい」と全部同じじゃないのだ", 7, "hands_a",
            "【二つの優しさ】テーブルの上で組んだ手に替え、感じの良さと時間のかかる誠実さを分ける"),
        img("会ったあとの段階で効くのは", 8, "hands_c", "【次章への渡し】組んだ手の別カットに替え、4分で見えるものがもう一つあるという予告へ"),
    ],
    # ---------------- S5 優しさの隣に、何が足りないのか（会ったあと②） ----------------
    5: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出す（②会ったあと ← いまここ）", telop=stage_board(2)),
        img("もう一つは、自分から前に出る力", 1, "open_c",
            "【自分から前に出る力】ゆったり座って話す人に替え、二本目のものさし（姿勢や発言で見せる）を直接描く"),
        img("優しい人の反対が", 2, "open_a", "【反対ではない】くつろいで話す人に替え、二つが別々のものさしである話を続ける"),
        diagram(
            "そのうえで、さっきの四つを思い出して",
            "【四つはどちらの列か】二本のものさしを列見出しにして、S2の四つが全部左の列に入り、右の列が空のままであることを見せる。決め文「一つも入っていないわ」で保持",
            sketch(
                [
                    [
                        cell("kind_h", icon="volunteer_activism", text="人に良くする力", at="そのうえで、さっきの四つを思い出して"),
                        cell("front_h", icon="campaign", text="自分から前に出る力", at="そのうえで、さっきの四つを思い出して"),
                    ],
                    [
                        cell("kind_1", text="犯罪・浮気をしない", at="犯罪をしない、浮気をしない", after="浮気をしない"),
                        cell("front_q", text="？", at="そのうえで、さっきの四つを思い出して"),
                    ],
                    [
                        cell("kind_2", text="働いている・優しい", at="犯罪をしない、浮気をしない", after="働いている"),
                        None,
                    ],
                ],
                highlight={"ids": ["front_q"], "at": "自分から前に出る力は", "after": "自分から前に出る力は"},
                caption={"text": "右の列に、入っているものがない", "at": "四つとも、さっき定義した二つ",
                         "after": "相手に誠実か"},
            ),
        ),
        img("あっ…", 3, "closed_b", "【受け】縮こまった姿勢のカットに替え、本当に入っていないという受けから姿勢の研究へ"),
        img("2016年、カリフォルニア大学バークレー校", 4, "chairs_c", "【姿勢の研究】スピードデート会場の椅子に替え、バークレー校の実験を紹介する",
            source="Vacharkulksemsuk et al. (2016) PNAS 113(15)"),
        img("体を開いた、ゆったりした姿勢", 5, "open_c", "【開いた姿勢】体を開いた姿勢の写真に戻り、1.76倍の結果を出す",
            telop="開いた姿勢 約1.76倍／アプリ 約1.27倍"),
        img("姿勢だけで", 6, "closed_a", "【対比の1枚】比較対象の縮こまった姿勢に切り替える（同一キュー内では切れないので、ずんだもんの驚きのキューで）"),
        img("待って", 7, "intimidate_c", "【威圧して従わせる】腕を組む人に替え、前に出る力の二種類のうち一方を見せる"),
        img("2025年、トロント大学", 8, "intimidate_a", "【短い関係だけ】腕を組む別カットに替え、威圧に惹かれるのは短期を探す人だけという結果へ",
            source="Witkower & Rule (2025) SPPS 17(5)"),
        img("長く続く関係を探している人は", 9, "respect_a", "【尊敬される方】人が集まって話を聞く場面に替え、どちらでもプラスな方を見せる"),
        img("会ったあとの段階で効くのは", 10, "respect_b", "【決め文の保持】聞き入る人たちの別カットに替え、三つ目が入っていないという決め文と間2.0秒を持たせる"),
        img("でも、なんで人は", 11, "open_b", "【次章への問い】身振りを交えて話す人に替え、なぜそこに惹かれるのかという問いで閉じる"),
    ],
    # ---------------- S6 なぜ、そこに惹かれるようにできているのか（起源） ----------------
    6: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出す（②会ったあと ← いまここ。4分で見えるものの話の続き）",
              telop=stage_board(2)),
        img("「人間の脳は石器時代から", 1, "stone_tools_a", "【石器時代】よく聞く言い方を、石器と古い道具の実物で受ける"),
        img("半分だけ、当たっているの", 2, "baby_parent_a", "【子育ての負担】赤ん坊の手を握る親の手に替え、妊娠と授乳を抱える側の負担の話へ"),
        img("1972年に提案された", 3, "baby_parent_b", "【親の投資】赤ん坊を抱く場面に替え、1972年の考え方を名前で出す",
            telop="「親の投資」（1972年）", source="Trivers (1972) Parental Investment and Sexual Selection"),
        diagram(
            "負担が重い側が相手を選ぶ側になり",
            "【古い仕組みの鎖】負担の差→選ぶ側と競う側→見て分かる手がかり、の順で黒板に書き足し、4分で見えるものに惹かれる理由をたどる",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "burden", "text": "子育ての負担が男女で違う", "icon": "child_care",
                     "at": "負担が重い側が相手を選ぶ側になり"},
                    {"id": "choose", "text": "重い側が選び軽い側が競う", "icon": "balance",
                     "at": "負担が重い側が相手を選ぶ側になり", "after": "相手を選ぶ側になり"},
                    {"id": "cue", "text": "見て分かる手がかりで選ぶ", "icon": "visibility",
                     "at": "だから、見て分かる手がかりが使われたの", "after": "見て分かる"},
                ],
                "caption": {"text": "仕組みは古い。中身は社会が決める", "at": "さっきの「尊敬される力」もここに入るわ"},
            },
        ),
        img("その敬意が、魅力として読まれるのよ", 4, "respect_a", "【敬意が魅力に】人が話に聞き入る場面に替え、敬意が魅力として読まれるところまで"),
        img("ここまでは、当たっている部分", 5, "stone_tools_a", "【折り返し】石器に戻し、ここから言い過ぎの部分に入ると宣言する（間1.0秒）"),
        img("まず「石器時代」は", 6, "stone_tools_b", "【一つの時代ではない】発掘の作業台に替え、EEA が特定の時代ではないという話へ"),
        img("それに、進化は止まっていない", 7, "wheat_a", "【農耕以降】麦畑に替え、農耕が始まってから選択が速まっているという報告を出す",
            telop="進化は止まっていない／農耕以降に選択が加速", source="Hawks et al. (2007) PNAS 104(52)"),
        img("そして何より、好みの中身は", 8, "street_couple_b", "【社会で動く】街を歩く男女に替え、平等な国ほど差が小さいという話へ",
            source="Zentner & Mitura (2012) Psychol Sci 23(10)"),
        img("じゃあ、どこが変わってなくて", 9, "street_couple_a", "【問い返し】街を歩く別カットに替え、どこが変わったのかという問いを受ける"),
        img("手がかりを素早く読む仕組みは", 10, "phone_c", "【決め文の保持】夜のスマホの手元に替え、会う仕組みだけが新しいという決め文と間2.5秒を持たせる"),
        img("読む側は昔のまま", 11, "hands_a", "【次章への問い】組んだ手に替え、時間がかかるものはいつ効くのかという問いで閉じる"),
    ],
    # ---------------- S7 続いてから効くものは、なぜ最初に見えないのか（続いてから） ----------------
    7: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出す（③続いてから ← いまここ）", telop=stage_board(3)),
        img("協調性と誠実性の高い人は", 1, "laughing_a", "【続いてからの段階】笑い合う二人で、関係が始まったあとの満足度の話に入る",
            telop="協調性・誠実性と満足度の相関 0.25〜0.29"),
        img("2010年、オーストラリアの", 2, "laughing_d", "【研究の帰属】和やかな別カットに替え、19調査をまとめた分析だと示す",
            telop="19の調査・3,848人をまとめた分析", source="Malouff et al. (2010) J Res Pers 44(1)"),
        img("そうね", 3, "watch_d", "【測っていないこと】待ち合わせで時計を見る人に替え、この研究の範囲の限定と間1.5秒を持たせる"),
        img("ここからは、研究そのものではなく", 4, "watch_a", "【推論の宣言】時計の別カットに替え、ここからは推論だと断る（約束を守る人かは4分では分からない）"),
        img("分からないのだ…", 5, "hands_c", "【時間がかかるもの】組んだ手に替え、何回か会ってやっと分かるという受けへ"),
        img("日本の実際のデータでも", 6, "meeting_a", "【日本のデータ】面談用の小さなテーブルと椅子に替え、追跡研究の規模を出す",
            telop="男性825人・女性757人を約1年4か月追跡"),
        img("大手の結婚相談サービスに", 7, "meeting_b", "【研究の帰属】面談室の別カットに替え、実施した研究チームを示す",
            source="鈴木翔・須藤康介・寺田悠希・小黒恵 (2018)『理論と方法』33(2)"),
        diagram(
            "お見合いを申し込まれた数で見ると",
            "【二つのものさし】同じ825人を申し込まれた数と結婚まで行ったかの二つで測ると、効く条件が食い違うことを見せる",
            sketch(
                [
                    [
                        cell("men", icon="groups", text="同じ825人の男性", at="お見合いを申し込まれた数で見ると"),
                        cell("offers", icon="forum", text="申し込まれた数", at="お見合いを申し込まれた数で見ると"),
                        cell("offers_res", text="学歴・収入・身長・体型", at="お見合いを申し込まれた数で見ると",
                             after="背が高い"),
                    ],
                    [
                        None,
                        cell("married", icon="favorite", text="結婚まで行ったか", at="実際に結婚まで行ったかどうかで見ると",
                             after="実際に結婚まで行ったかどうかで見ると"),
                        cell("married_res", text="収入以外は効かない", at="実際に結婚まで行ったかどうかで見ると",
                             after="学歴も身長も体型も"),
                    ],
                ],
                arrows=[("men", "offers"), ("men", "married"), ("offers", "offers_res"), ("married", "married_res")],
                highlight={"ids": ["married_res"], "at": "例外は収入だけ"},
            ),
        ),
        img("この研究が言えるのは", 8, "meeting_c", "【言えるところまで】面談室の別カットに替え、研究が言える範囲を区切る"),
        img("そこに、さっきの推論を重ねると", 9, "watch_a", "【決め文の保持】時計に戻し、効き始めるのが遅いという決め文と間2.5秒を持たせる"),
        img("遅いなら、その時間は", 10, "hands_c", "【次章への問い】組んだ手に替え、その時間はどこで手に入れるのかという問いで閉じる"),
    ],
    # ---------------- S8 その「時間」は、誰が用意していたのか（会う前・歴史） ----------------
    8: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出す（①会う前 ← いまここ。出会い方そのものの話へ戻る）",
              telop=stage_board(1)),
        img("明治より前の村では", 1, "wedding_b", "【家が決める結婚】古い和装の記念写真で、明治の民法の話に入る",
            telop="明治民法「戸主ノ同意」", source="明治民法 第750条／阪井裕一郎『仲人の近代』青弓社 2021"),
        img("本人の気持ちだけじゃ", 2, "venue_a", "【仲人が間に立った】結婚式場に替え、保証と段取りを担った役の説明へ"),
        img("慶應義塾大学の准教授", 3, "venue_b", "【近代の制度】式場の別カットに替え、見合い結婚が近代の制度だという研究を示す",
            source="阪井裕一郎『仲人の近代』青弓社 2021（慶應義塾大学 准教授）"),
        img("1947年、憲法に", 4, "wedding_b", "【本人が選ぶものへ】記念写真に戻し、憲法24条で結婚が本人のものになったことを出す",
            telop="憲法24条「両性の合意のみ」（1947年）", source="日本国憲法 第24条"),
        img("それでも仲人の慣行は", 5, "venue_a", "【7年でほぼ消えた】式場に替え、仲人を立てた割合の急落を数字で出す",
            telop="仲人を立てた割合 1994年63.9%→2001年7.3%",
            source="小関孝子 (2019) 社会デザイン学会学会誌 11（ゼクシィ結婚トレンド調査 2004）"),
        img("7年で、63パーセントから", 6, "venue_b", "【驚きの受け】式場の別カットに替え、ずんだもんの驚きで一拍置く"),
        img("出会い方も同じ向きに動いたわ", 7, "wedding_b", "【見合いの減少】記念写真に戻し、69.0%から9.9%への落差を出す",
            telop="見合い結婚 69.0% → 9.9%", source=IPSS),
        img("かわりにネットで出会った夫婦が", 8, "phone_c", "【ネットの増加】夜のスマホの手元に替え、ネットが見合いを追い抜いたことを出す",
            telop="ネットで出会う 15.2%"),
        diagram(
            "見合いと仲人には",
            "【誰が用意していたか】周りの人の保証と、何度も会う時間の二つが、昔は先に付いていたことを収束で見せる。決め文で保持",
            {
                "type": "narrative",
                "layout": "converge",
                "items": [
                    {"id": "vouch", "text": "周りの人の保証", "at": "周りの人の保証と、何度も会う時間",
                     "after": "周りの人の保証"},
                    {"id": "time", "text": "何度も会う時間", "at": "周りの人の保証と、何度も会う時間",
                     "after": "何度も会う"},
                ],
                "result": {"text": "昔は先に付いていた", "at": "まともさが効き始めるまでの時間を",
                           "after": "他人が用意して"},
            },
        ),
        img("鋭いわね", 9, "university_c", "【婚活という言葉】大学の校舎に替え、2008年に婚活を提唱した研究者を示す",
            source="山田昌弘・白河桃子『「婚活」時代』ディスカヴァー 2008（山田＝中央大学 教授）"),
        img("「モテる」が切実な言葉に", 10, "phone_a", "【自分で見せる市場】夜のスマホの手元に替え、モテが切実になった理由へ"),
        img("昔がよかった", 11, "venue_b", "【留保】式場に替え、昔がよかったという話ではないという断りを置く"),
        img("僕はずっと、その市場の", 12, "cafe_window_b", "【章末の問い】カフェの窓際に替え、結局何に負けているのかという問いで閉じる"),
    ],
    # ---------------- S9 結び（真のモテ要素とは何か） ----------------
    9: [
        img(None, 1, "commute_c", "【結びの整理】朝の通りの絵で、冒頭の一行に戻る"),
        board("会う前。", "【段階ごとの答え①】会う前は誠実さまで確認できない、を黒板に書く",
              telop=answer_board(1)),
        board("会ったあと。", "【段階ごとの答え②】会ったあとに効く三つを書き足す", telop=answer_board(2)),
        board("続いてから。", "【段階ごとの答え③】続いてから効くものを書き足し、三段そろえる", telop=answer_board(3)),
        img("そう。", 2, "venue_a", "【薄くなった仕組み】結婚式場に替え、時間を用意してくれていた仕組みが薄くなった話へ"),
        img("まともさが弱いから", 3, "group_g", "【決め文の保持】人が集まって声を合わせる場面に替え、判断が終わる場面が増えたという決め文と間2.5秒を持たせる"),
        img("だから、うまくいっていないことを", 4, "group_b", "【人格のせいにしない】人が輪になって同じ作業をする場面に替え、断りを添える"),
        img("まともさは、持っているだけでは", 5, "group_g", "【決め文の保持】声を合わせる場面に戻し、伝わる場所まで行くという決め文と間2.5秒を持たせる"),
        img("僕、プロフィールだけを", 6, "group_b", "【方針の転換】輪になる場面に替え、書き直すのをやめると言うところまで"),
        img("書き直すより", 7, "group_f", "【象徴的な最後の一枚】手仕事を教え合う場面で終え、アウトロへつなぐ"),
    ],
}


def regenerate_yaml() -> None:
    """台本 md から YAML（narration 部）を作り直す（ビートを貼る前に毎回実行する）。"""
    cmd = [
        sys.executable,
        str(REPO / "tools" / "kamishibai_md_to_yaml.py"),
        str(MD_PATH),
        "--v5-yaml", str(HERE / "empty-v5-stub.yaml"),
        "--out", str(YAML_PATH),
        "--bgm", "../bgm/meisou-no-piano.mp3",
        "--bgm-credit", "BGM:「瞑想のピアノ」lei（DOVA-SYNDROME）",
        "--puppet-sink", "0.12",
        "--tempo", "1.1",
    ]
    subprocess.run(cmd, check=True, cwd=str(REPO))


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
    regenerate_yaml()
    doc = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    total = 0
    for scene in doc["scenes"]:
        sid = scene["id"]
        cues = cues_of(scene)
        beats = []
        last_from = 0
        img_i = 0
        for kind, anchor, slot, ckey, why, telop, source in BEATS[sid]:
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
                b["credit"] = f"{source}／{CREDIT[ckey]}" if source else CREDIT[ckey]
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
