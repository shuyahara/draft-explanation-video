"""めたん×ずんだもん版・「なぜ"誠実な"男性はモテないのか」**v7（10シーン）**: ビート
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
v7 の設計メモ（2026-09-12。v6=9シーン から 10シーン へ改稿）
---------------------------------------------------------------------------
■ 道しるべの板（全編の骨格）
  S2 で「三つの段階」を黒板に書き、以後 **各章の頭で同じ板を 5〜10 秒ほど出し、その章の段階の
  行を `highlight_lines` で金色にする**（S3=①会う前 / S4=②初対面 / S5=② / S7=③長い関係 /
  S8=③）。v6 までの「← いまここ」の文字は廃止した（2026-09-12。script-to-video の
  `board.highlight_lines`。見出しが1行目なので、段階 n は n+1 行目）。S6（起源）と S9（歴史）は
  段階の外の話なので道しるべを出さない。S10 は別の板「段階ごとの答え」を 1 行ずつ足す（3 枚）。

  板の尺: `board` ビートは次のビートまでが尺になるので、章頭の板は本文の最初の 1〜2 キューを
  覆う位置に次の image ビートを置いている（preflight の複数行ボード上限 20 秒）。

  S2 の板は 3 枚（「誠実さ」の定義 → 三つの段階の提示 → 結論の二文）。三つの段階の提示から
  結論の二文まで通しで板にすると 20 秒を超えるため、間に ずんだもん の受けを写真ではさんでいる。

■ 図解 6 箇所（台本の指定どおりの型。隣接する図解で同じ layout を使っていない）
  S3 sketch(2行3列) → S4 chart → S5 sketch(3行2列) → S6 chain → S7 sketch(2行2列) → S9 converge
  sketch は 3 回だが格子の形が全部違うので、同型反復リント（型＋格子の形で数える）には掛からない。

■ ツール側の制約で台本の字面から詰めたところ（**ナレーションは 1 文字も変えていない**）
  - `narrative` のラベルは 12 文字まで（`NARRATIVE_LABEL_MAX_LENGTH`）。S6 chain の 4 段は
    台本の字面（「負担が重い側」「選ぶ側になる」「短い時間で見きわめる」「見える手がかり
    （健康・力・尊敬）」）のうち 4 段目が 15 字あるため、括弧の中身を caption
    「健康・力・尊敬されている」へ回した。
  - `chart` の値ラベルは小数1桁に丸められる（`_format_chart_value`）。S4 は 0.46/0.32/0.16 が
    0.5/0.3/0.2 と出てしまうため、項目ラベル側に値を入れた（台本の「ラベルに値を含める」の
    指定どおり）。label は 8 文字以内。
  - `sketch` は行3・列4・セル12 が上限、セル本文は 12 文字まで。S7 の「見た目の釣り合い 0.72」は
    14 字あるので「釣り合い 0.72」に詰めた（語は台本のまま）。
  - 1行 telop（image ビート）は自動縮小されないので 30 字以内に収め、**研究の出典（著者・年・
    誌名）は `credit`（字幕帯右下の小文字）へ**回した（`img(..., source=...)`）。
  - ビート境界はキュー境界にしか置けないので、同一キュー内の対比（S5 の「開いた姿勢 →
    縮こまった姿勢」）は次のキュー（ずんだもんの「姿勢だけで！？」）で切り替えている。

■ 章カード 6 枚（S3・S5・S6・S7・S8・S9）
  `lint.CHAPTER_CARD_MAX_COUNT` は 5 なので validate が「章カードが6回あります」と警告する。
  台本 v7（章のつなぎレビュー反映）が 6 枚を指定しているため、**警告を承知で 6 枚のまま**に
  してある（減らすなら S6「なぜ、見た目と自信に惹かれるのか」が候補。要判断）。

■ 貼り写真
  台本が名指ししたファイルは指定の位置で使い、尺を分けるための前後のカットは同じモチーフの
  別候補（manifest-s01-s07 / s08-s14 / references/20260912-s7-photo-credits.md）から採った。
  S7（長い関係①）の 6 枚は v7 で新規に取得（`s15_*`）。
  同一ファイルは動画全体で 3 ビートまで。シーンをまたぐ再利用は意味のある回収だけ
  （夜のスマホ＝会う前 / 組んだ手＝時間のかかる誠実さ / 婚礼写真・式場＝用意されていた時間）。
  `s02_commute_d` は車両に "New York Sub..." の表示が写り都市が特定できるため採らなかった。
  `illust/s11_1930s_wedding_a.png` は顔が描き込まれているため不採用（b のみ使う）。
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
    "phone_c": "Photo: Jaroslav Maler / Pexels",  # 原綴 Maléř。ř が黒板フォントで□になるため ASCII 表記
    "phone_a": "Photo: Mikhail Nilov / Pexels",
    "phone_a": "Photo: Phil Desforges / Pexels",
    "cafe_a": "Photo: Ibrahim KARASU / Pexels",  # 原綴 İbrahim。İ が□になるため ASCII 表記
    "cafe_c": "Photo: Seydanur Yildiz / Pexels",  # 原綴 Şeydanur Yıldız。Ş・ı が□になるため ASCII 表記
    "bbs_board": "Illustration: AI generated",
    "commute_e": "Photo: Ahmad Shakir Shamsulbadri / Pexels",
    "commute_c": "Photo: Airam Dato-on / Pexels",
    "commute_d": "Photo: Lara Jameson / Pexels",
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
    "hands_b": "Photo: cottonbro studio / Pexels",
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
    "chairs_b": "Photo: Pixabay",
    "chairs_c": "Photo: Pixabay",
    "group_g": "Photo: Thirdman / Pexels",
    "group_f": "Photo: Nataliya Vaitkevich / Pexels",
    "group_b": "Photo: cottonbro studio / Pexels",
    "group_a": "Photo: Pixabay",
    "group_d": "Photo: THE MACDUFFIE SCHOOL / Pexels",
    # v4 で新規に取得した分（S6 の起源の章・S9 の歴史の章）
    "stone_tools_a": "Photo: Rinat Askarov / Pexels",
    "stone_tools_b": "Photo: Yena Kwon / Pexels",
    "baby_parent_a": "Photo: Han Lahandoe / Pexels",
    "baby_parent_b": "Photo: Pixabay",
    "wheat_a": "Photo: Pixabay",
    "street_couple_a": "Photo: Leticia Curvelo / Pexels",
    "street_couple_b": "Photo: Pixabay",
    "venue_a": "Photo: Steven Van Elk / Pexels",
    "venue_b": "Photo: Kimy Moto / Pexels",
    # v7 で新規に取得した分（S7 長い関係①。references/20260912-s7-photo-credits.md）
    "friends_laughing_a": "Photo: Vitaly Gariev / Pexels",
    "friends_laughing_b": "Photo: William Fortunato / Pexels",
    "friends_walking_a": "Photo: Liliana Drew / Pexels",
    "friends_walking_b": "Photo: Felicity Tai / Pexels",
    "couple_hands_a": "Photo: Nicole Lima / Pexels",
    "couple_hands_b": "Photo: Gihan Bandara / Pexels",
}

# 採用元ファイル（candidates-matome/{相対パス}）→ render-assets へ配置するときの対応。
SOURCE_FILE = {
    "phone_c": "stock/s01_phone_c.jpg",
    "phone_a": "stock/s01_phone_b.jpg",
    "phone_a": "stock/s01_phone_a.jpg",
    "cafe_a": "stock/s01_cafe_a.jpg",
    "cafe_c": "stock/s01_cafe_c.jpg",
    "bbs_board": "illust/ill_bulletin_board.png",
    "commute_e": "stock/s02_commute_e.jpg",
    "commute_c": "stock/s02_commute_c.jpg",
    "commute_d": "stock/s02_commute_d.jpg",
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
    "hands_b": "stock/s08_hands_table_b.jpg",
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
    "chairs_b": "stock/s12_facing_chairs_b.jpg",
    "chairs_c": "stock/s12_facing_chairs_c.jpg",
    "group_g": "stock/s14_group_activity_g.jpg",
    "group_f": "stock/s14_group_activity_f.jpg",
    "group_b": "stock/s14_group_activity_b.jpg",
    "group_a": "stock/s14_group_activity_a.jpg",
    "group_d": "stock/s14_group_activity_d.jpg",
    "stone_tools_a": "stock/s06_stone_tools_a.jpg",
    "stone_tools_b": "stock/s06_stone_tools_b.jpg",
    "baby_parent_a": "stock/s06_baby_parent_a.jpg",
    "baby_parent_b": "stock/s06_baby_parent_b.jpg",
    "wheat_a": "stock/s06_wheat_a.jpg",
    "street_couple_a": "stock/s06_street_couple_a.jpg",
    "street_couple_b": "stock/s06_street_couple_b.jpg",
    "venue_a": "stock/s08_wedding_venue_a.jpg",
    "venue_b": "stock/s08_wedding_venue_b.jpg",
    "friends_laughing_a": "stock/s15_friends_laughing_a.jpg",
    "friends_laughing_b": "stock/s15_friends_laughing_b.jpg",
    "friends_walking_a": "stock/s15_friends_walking_a.jpg",
    "friends_walking_b": "stock/s15_friends_walking_b.jpg",
    "couple_hands_a": "stock/s15_couple_hands_a.jpg",
    "couple_hands_b": "stock/s15_couple_hands_b.jpg",
}

# 台本「発音・ポーズメモ」の読み。**登録は最小限**にする（VOICEVOX が正しく読む語を登録すると
# 複合語の読みが壊れる。memory/voicevox-user-dict-priority.md）。ここに入れていない語
# （威圧・准教授・人格・石器時代・小数点の数値など）は preflight の読み突合で確認する。
# surface に助詞は含めない（辞書の読みに書くと「ハ」と発音されてしまうため）。
GLOBAL_READINGS = [
    ("顔がいい方", "カオガイイホウ"),
    ("感じのいい方", "カンジノイイホウ"),
    ("やり方", "ヤリカタ"),
    ("親の投資", "オヤノトウシ"),
    ("戸主", "コシュ"),
    ("仲人", "ナコウド"),
    ("基いて", "モトヅイテ"),
    ("阪井裕一郎", "サカイユウイチロウ"),
    # preflight の読み突合で VOICEVOX が読み違えたもの（2026-09-12 実測）。
    ("明星大学", "ミョウジョウダイガク"),  # VOICEVOX は「メエセエダイガク」と読む
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 台本「発音・ポーズメモ」のうち（間 N）で明示済みでないもの（生成側の既定値＝話者交代0.45・
# 文境界0.35・章末1.2 から動かす箇所だけ）。pause_after はセグメント末尾に効くので、
# セグメント末尾の一文で照合する。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [("損をするのだ", 0.9)],
}

# 道しるべの板（S2 で提示し、以後の章頭で該当の段階の行を金色にして再掲する）。
STAGE_BOARD_LINES = [
    "三つの段階",
    "①会う前＝写真とプロフィール",
    "②初対面＝会って数回まで",
    "③長い関係＝付き合いが続いてから",
]
STAGE_BOARD = "\n".join(STAGE_BOARD_LINES)


def stage_here(stage: int) -> list[int]:
    """段階 `stage`（1〜3）の行番号（1始まり）。見出しが1行目なので stage+1 行目になる。"""
    return [stage + 1]


# S2 の板「誠実さ」の中身（章頭。以後の章が参照する言葉を固定する）。
SINCERITY_BOARD = "\n".join([
    "誠実さ",
    "①嘘をつかない",
    "②約束を守る",
    "③困ったときに逃げない",
])

# S5 の板「自信の見せ方」（「二種類あるの」から3キューぶん）。
CONFIDENCE_BOARD = "\n".join([
    "自信の見せ方",
    "①威圧して従わせる＝短い関係だけ",
    "②能力で尊敬される＝どちらにも有利",
])

# S8 の板（「まだ半分よ」から3キューぶん）。
OFFER_BOARD = "\n".join([
    "申し込まれる段階と、結ばれる段階",
    "①申し込まれる＝学歴・収入・身長・体型",
    "②結婚まで行く＝収入だけ",
])


# S10 の板「段階ごとの答え」（ナレーションの順＝会う前→初対面→長い関係 に 1 行ずつ足す）。
ANSWER_BOARD_LINES = [
    "段階ごとの答え",
    "①会う前＝誠実さまでは確認できない",
    "②初対面＝見た目・人当たり・自信と積極性",
    "③長い関係＝誠実さが有利に働く",
]


def answer_board(n: int) -> str:
    """「段階ごとの答え」の板を、見出し＋先頭 n 行ぶんで作る。"""
    return "\n".join(ANSWER_BOARD_LINES[: n + 1])


def img(anchor, slot, credit_key, why, telop=None, source=None):
    """source は研究の出典（著者・年・誌名）。写真クレジットと一緒に字幕帯右下の小文字へ出す
    （telop は30字以内に収める規約のため、出典は telop ではなく credit 側に置く）。"""
    return ("image", anchor, slot, credit_key, why, telop, source, None)


def board(anchor, why, telop=None, highlight_lines=None):
    """黒板文字だけのビート。`highlight_lines` は金色にする行番号（1始まり）。"""
    return ("board", anchor, None, None, why, telop, None, highlight_lines)


def chapter():
    return ("chapter", None, None, None, "【章の入口】黒板に問いを書いて本題へ", None, None, None)


def diagram(anchor, why, spec):
    """チョーク図解。spec 内の `at` は文字列アンカーで書き、実行時にキュー番号へ解決する。"""
    return ("diagram", anchor, None, None, why, spec, None, None)


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
        img(None, 1, "phone_c", "【半年の書き直し】夜の部屋でスマホを見る手元から始める（台本指定の静止画）。性別設定の注記は小さく（クレジット欄）",
            source="※本動画ではずんだもんは男の子という設定です"),
        img("それで、成立したマッチは", 2, "phone_a",
            "【数字】手元の別カットに替え、マッチ3件の数字を台詞と同時にテロップで出す",
            telop="半年でマッチ3件"),
        img("実際に会えたのは1人で", 3, "cafe_a",
            "【会ったあとで止まった1件】二人分のカップに替え、会えた1人の話からめたんの受けまで",
            telop="会えたのは1人"),
        img("掲示板には", 4, "bbs_board", "【掲示板の書き込み】「誠実な男ほどモテない」を見た画面（文字は描かない）"),
        img("一緒に確かめましょう", 5, "cafe_c", "【問いの言語化】カフェのカットに替え、この動画が答える問いを立てる"),
        img("誠実さが嫌われている", 6, "cafe_a", "【答えの形の予告】二人分のカップに戻し「嫌われてはいない／確かめようがない」を予告"),
        img("嫌われてはいない", 7, "phone_a", "【間】手元に戻り、ずんだもんが違いを飲み込めないところまで尺を分ける"),
    ],
    # ---------------- S2 三つの段階 ----------------
    2: [
        board(None, "【用語の定義】この動画で言う誠実さの中身を黒板に固定し、以後の章が参照できるようにする",
              telop=SINCERITY_BOARD),
        img("そして、この話は段階を分けないと混ざるの", 1, "commute_e",
            "【段階分けの前置き】朝の駅のホームに替え、出会いから付き合いが続くまでを三つに分ける宣言へ"),
        board("一つ目は、会う前",
              "【全編の骨格】三つの段階を黒板に書き、以後の章頭で参照できるようにする",
              telop=STAGE_BOARD),
        img("この三つで、選ばれやすくなる要素が違うの", 2, "phone_a",
            "【当事者の位置】夜のスマホの手元に替え、会う前でも初対面でも止まっているという受けへ"),
        board("誠実さが有利に働くのは",
              "【主軸の三文】台本「演出」の指定どおり、結論の二文は板を保持したまま言う（間1.0→1.5）",
              telop=STAGE_BOARD),
        img("途中で、よく聞く常識が三つ", 3, "commute_d",
            "【予告】街を歩く人々に替え、この先ひっくり返る三つの常識を並べる"),
        img("ここから、会う前、初対面", 4, "commute_e",
            "【順番の宣言】駅のホームに戻し、三つの段階を順に確かめると告げて章へ渡す"),
        img("確かめようがないだけなら", 5, "phone_c",
            "【次章への問い】夜のスマホの手元に替え、会う前から嫌われているのではという問いで閉じる"),
    ],
    # ---------------- S3 感じのいい男は、会う前に損をするのか（会う前） ----------------
    3: [
        chapter(),
        board(None, "【道しるべ】章頭に三つの段階の板を出し、この章が①会う前の話だと示す",
              telop=STAGE_BOARD, highlight_lines=stage_here(1)),
        img("それが損になるのか", 1, "facetoface_b",
            "【二人の男性】カフェで向かい合う男性二人に替え、2003年の実験の組み立てに入る",
            source="Urbaniak & Kilmann (2003) Sex Roles 49(9/10)"),
        diagram(
            "たとえば、見た目は良いけれど",
            "【実験の骨格】二人の男性→女子学生に聞いた→感じがいい方が選ばれた、を格子で見せる",
            sketch(
                [
                    [
                        cell("mean_man", icon="person", text="見た目◎ 意地悪", at="たとえば、見た目は良いけれど"),
                        cell("ask", icon="forum", text="女子学生に聞いた", at="顔がいい方なのだ"),
                        cell("chosen", icon="thumb_up", text="感じがいい方が選ばれた",
                             at="選ばれたのは、感じがいい方だったの", after="選ばれたのは"),
                    ],
                    [
                        cell("nice_man", icon="person", text="見た目△ 感じがいい",
                             at="たとえば、見た目は良いけれど", after="見た目は劣るけれど"),
                        None,
                        None,
                    ],
                ],
                arrows=[("mean_man", "ask"), ("nice_man", "ask"), ("ask", "chosen")],
            ),
        ),
        img("えっ、顔がいい方が負けた", 2, "university_b",
            "【再現性】大学の校舎に替え、二度の実験の人数を出す",
            telop="感じがいい方が選ばれた（N=48／N=194）"),
        img("でも、見た目の力と態度の力が", 3, "university_c",
            "【交絡への疑問】別の校舎の絵に替え、感じの良さだけの力かという疑問と、その答えまで"),
        img("評価が低かったのは", 4, "laughing_d",
            "【決め文の保持】和やかに話す二人に替え、会う前でも負けていないという決め文と間2.0秒を持たせる"),
        img("伝わりさえすれば…", 5, "cafe_window_a",
            "【章末の問い】カフェの窓際に替え、自分のプロフィールは伝わっていたのかという問いへ"),
    ],
    # ---------------- S4 初対面で有利なのは、何か（初対面①） ----------------
    4: [
        board(None, "【道しるべ】章カードは無いがここから段階が変わるので、冒頭に板を出す（②初対面）",
              telop=STAGE_BOARD, highlight_lines=stage_here(2)),
        img("ノースウェスタン大学のポール", 1, "facetoface_a", "【実験へ】向かい合う男女の席に替え、スピードデートの実験に入る",
            source="Eastwick & Finkel (2008) JPSP 94(2)"),
        img("まず全員に、理想の相手に", 2, "chairs_c", "【手順と人数】会場の椅子に替え、4分ずつ9〜13人と会う手順を出す",
            telop="163人／一人4分ずつ 9〜13人と"),
        img("会う前に書いたとおりの人を", 3, "chairs_a", "【当たらなかった】会場の別カットに替え、書いた理想が当たらなかったところまで"),
        diagram(
            "じゃあ、実際には何に惹かれてたのだ",
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
        img("1に近いほど、強いのだ", 4, "chairs_a", "【相関係数の説明】会場の椅子に戻し、0と1の意味を言い終えるところまで"),
        img("初対面でいちばん有利に働いたのは", 5, "cafe_window_b",
            "【決め文の保持】カフェの窓際に替え、見えるものが勝つ段階だという決め文と間1.5秒を持たせる"),
        img("ただ、二番目の人当たりの良さは", 6, "laughing_a",
            "【人当たりの良さ】笑いながら話す二人に替え、二番目の人当たりが稼ぐ力より上だと言う"),
        img("ただし、ここで測った", 7, "laughing_d",
            "【言葉の限定】和やかに話す二人に替え、測ったのは話していて感じがいいという評価だけだと限定する"),
        img("誠実さとは、別なのだ", 8, "hands_a",
            "【二つの優しさ】テーブルの上で組んだ手に替え、すぐ見える人当たりと時間がかかる誠実さを分ける"),
        img("初対面で有利に働くのは、すぐ見える方だけよ", 9, "hands_c",
            "【次章への渡し】組んだ手の別カットに替え、初対面で有利なものがもう一つあるという予告へ"),
    ],
    # ---------------- S5 自信と積極性、そして「悪い男」（初対面②） ----------------
    5: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出す（②初対面）",
              telop=STAGE_BOARD, highlight_lines=stage_here(2)),
        img("優しさ、誠実さ、思いやり", 1, "laughing_a",
            "【二本のものさし】笑いながら話す二人に替え、人に良くする力と自信と積極性の二本を提示する"),
        img("優しい人の反対が", 2, "open_a",
            "【反対ではない】ゆったり座って話す人に替え、二つが別々のものさしである話を続ける"),
        diagram(
            "そして、最初に決めた誠実さの中身を",
            "【誠実さはどちらの列か】二本のものさしを列見出しにして、誠実さの三つが全部左の列に入り、右の列が空のままであることを見せる。決め文「入っていないわ」で保持",
            sketch(
                [
                    [
                        cell("kind_h", icon="volunteer_activism", text="人に良くする力",
                             at="そして、最初に決めた誠実さの中身を"),
                        cell("front_h", icon="campaign", text="自信と積極性",
                             at="そして、最初に決めた誠実さの中身を"),
                    ],
                    [
                        cell("kind_1", text="嘘をつかない", at="嘘をつかない、約束を守る", after="嘘をつかない"),
                        cell("front_q", text="？", at="そして、最初に決めた誠実さの中身を"),
                    ],
                    [
                        cell("kind_2", text="約束を守る 逃げない", at="嘘をつかない、約束を守る", after="逃げない"),
                        None,
                    ],
                ],
                highlight={"ids": ["front_q"], "at": "この中に、自信と積極性は", "after": "自信と積極性"},
                caption={"text": "右の列に、入っているものがない", "at": "この中に、自信と積極性は"},
            ),
        ),
        img("そして自信と積極性は、会った瞬間に", 3, "facetoface_a",
            "【姿勢の研究】向かい合う男女の席に替え、バークレー校の実験を紹介する",
            source="Vacharkulksemsuk et al. (2016) PNAS 113(15)"),
        img("体を開いた、ゆったりした姿勢", 4, "open_c", "【開いた姿勢】体を開いた姿勢の写真に替え、1.76倍の結果を出す",
            telop="姿勢が開いていた人は 約1.76倍 選ばれた"),
        img("姿勢だけで", 5, "intimidate_c", "【胸を張って腕を組む】自信を見せようと意気込む姿に切り替える（同一キュー内では切れないので、ずんだもんの驚きのキューで）"),
        img("聞いたことあるのだ", 6, "intimidate_a", "【悪い男の説】腕を組む人に替え、悪い男の方がモテるという説を受け止めて待ったをかける"),
        board("自信の見せ方には、二種類あるの",
              "【二種類の見せ方】威圧と尊敬の違いを黒板に書き、次の研究の結果を読む前提にする",
              telop=CONFIDENCE_BOARD),
        img("威圧するやり方に惹かれるのは", 7, "intimidate_c", "【短い関係だけ】腕を組む別カットに替え、威圧に惹かれるのは短期を探す人だけという結果へ",
            telop="威圧型＝短い関係を探す人にだけ有利",
            source="Witkower & Rule (2025) SPPS 17(5)"),
        img("尊敬されるやり方は", 8, "respect_a", "【尊敬される方】人が集まって話を聞く場面に替え、どちらにも有利な方を見せる"),
        img("初対面で有利に働くのは、見た目と", 9, "respect_b",
            "【決め文の保持】聞き入る人たちの別カットに替え、誠実さが入っていないという決め文と間2.0秒を持たせる"),
        img("でも、なんで人は", 10, "open_b", "【次章への問い】身振りを交えて話す人に替え、なぜそこに惹かれるのかという問いで閉じる"),
    ],
    # ---------------- S6 なぜ、見た目と自信に惹かれるのか（起源） ----------------
    6: [
        img(None, 1, "stone_tools_a", "【石器時代】よく聞く言い方を、石器と古い道具の実物で受ける"),
        img("聞いたことあるのだ", 2, "stone_tools_b", "【受け】発掘の作業台に替え、見た目と強さで選ばれるという通説の確認まで"),
        img("半分だけ、当たっているの", 3, "baby_parent_a", "【子育ての負担】赤ん坊の手を握る親の手に替え、妊娠と授乳を抱える側の負担の話へ"),
        img("1972年に提案された", 4, "baby_parent_b", "【親の投資】赤ん坊を抱く場面に替え、1972年の考え方を名前で出す",
            telop="「親の投資」（1972年）", source="Trivers (1972) Parental Investment and Sexual Selection"),
        diagram(
            "負担が重い側が相手を選ぶ側になり",
            "【古い仕組みの鎖】負担の差→選ぶ側→短い時間で見きわめる→見える手がかり、の順で黒板に書き足し、4分で見えるものに惹かれる理由をたどる",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "burden", "text": "負担が重い側", "icon": "child_care",
                     "at": "負担が重い側が相手を選ぶ側になり"},
                    {"id": "choose", "text": "選ぶ側になる", "icon": "balance",
                     "at": "負担が重い側が相手を選ぶ側になり", "after": "選ぶ側になり"},
                    {"id": "quick", "text": "短い時間で見きわめる", "icon": "timer",
                     "at": "選ぶ側は、相手を短い時間で", "after": "短い時間で"},
                    {"id": "cue", "text": "見える手がかり", "icon": "visibility",
                     "at": "だから、見て分かる手がかりが", "after": "見て分かる"},
                ],
                "caption": {"text": "健康・力・尊敬されている", "at": "健康そうか、力がありそうか"},
            },
        ),
        img("4分で見えるものに惹かれるのは", 5, "chairs_c", "【折り返し】スピードデート会場の椅子に替え、ここから言い過ぎの部分に入ると宣言する（間1.0秒）"),
        img("相手に求める条件は", 6, "street_couple_b", "【社会で動く】街を歩く男女に替え、平等な国ほど差が小さいという話から、どこが変わったのかという問いまで",
            source="Zentner & Mitura (2012) Psychol Sci 23(10)"),
        img("残っているのは", 7, "phone_c", "【決め文の保持】夜のスマホの手元に替え、出会い方だけが新しいという決め文と間2.5秒を持たせる"),
        img("判断する癖は古くて", 8, "hands_a", "【次章への問い】組んだ手に替え、時間がかかるものはいつ有利になるのかという問いで閉じる"),
    ],
    # ---------------- S7 恋は、いつ始まるのか（長い関係①） ----------------
    7: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出す（③長い関係）",
              telop=STAGE_BOARD, highlight_lines=stage_here(3)),
        img("まず、恋人どうしは", 1, "friends_laughing_a", "【いつ恋に落ちるか】カフェで笑い合う友人たちに替え、7つの調査をまとめた分析に入る",
            source="Stinson, Cameron & Hoplock (2022) SPPS 13(2)"),
        img("出会ってすぐ", 2, "friends_walking_b", "【3人に2人】並んで歩く二人に替え、付き合う前に友人だった人が68パーセントという数字を出す",
            telop="付き合う前に友人だった 68%"),
        img("3人に2人が、友達からなのだ", 3, "friends_laughing_b", "【友人でいた期間】屋外で談笑する場面に替え、平均約2年・7割は恋愛目的ではなかったところまで"),
        img("初対面で決まってるわけじゃ", 4, "friends_walking_b", "【もう一つの研究へ】並んで歩く別カットに替え、次の研究に渡す"),
        img("167組のカップルに", 5, "couple_hands_a", "【167組】手をつなぐ手元に替え、付き合う前にどれくらい知り合いだったかを聞いた研究を示す",
            source="Hunt, Eastwick & Finkel (2015) Psychol Sci 26(7)"),
        diagram(
            "知り合って1か月以内に",
            "【時間と釣り合い】知り合ってすぐの交際と、9か月以上たってからの交際を上下に並べ、見た目の釣り合いが消えることを見せる",
            sketch(
                [
                    [
                        cell("early", icon="bolt", text="1か月以内に交際", at="知り合って1か月以内に"),
                        cell("early_r", text="釣り合い 0.72", at="相関で0.72よ", after="0.72"),
                    ],
                    [
                        cell("late", icon="hourglass_empty", text="9か月以上で交際",
                             at="ところが、付き合う前に9か月以上", after="9か月以上"),
                        cell("late_r", text="釣り合い なし",
                             at="ところが、付き合う前に9か月以上", after="見た目の釣り合い"),
                    ],
                ],
                arrows=[("early", "early_r"), ("late", "late_r")],
            ),
        ),
        img("9か月で、見た目が関係なくなる", 6, "cafe_window_a",
            "【決め文の保持】カフェの窓際に替え、知り合う時間が長いほど見た目以外で選ばれるという決め文と間2.0秒を持たせる",
            telop="1か月以内 0.72／9か月以上 消える"),
        img("じゃあ、その「見た目以外のもの」", 7, "couple_hands_b", "【次章への問い】手をつなぐ別カットに替え、それが誠実さなのかという問いで閉じる"),
    ],
    # ---------------- S8 長い関係で有利なのは、誠実さ（長い関係②） ----------------
    8: [
        chapter(),
        board(None, "【道しるべ】章頭に板を出す（③長い関係）",
              telop=STAGE_BOARD, highlight_lines=stage_here(3)),
        img("性格検査で測った協調性と誠実性", 1, "hands_b", "【二つの性格】テーブルで手を組む場面に替え、協調性と誠実性を日本語で言い直すところまで"),
        img("19の調査、合わせて", 2, "university_b", "【研究の帰属】大学の校舎に替え、19調査をまとめた分析と実施者を示す",
            telop="19の調査・3,848人をまとめた分析", source="Malouff et al. (2010) J Res Pers 44(1)"),
        img("協調性と誠実性！", 3, "hands_c", "【測っていないこと】組んだ手の別カットに替え、この研究の範囲の限定と間1.5秒を持たせる"),
        img("ここからは研究結果ではなく", 4, "watch_a", "【推論の宣言】待ち合わせで時計を見る人に替え、ここからは推論だと断る"),
        img("分からないのだ…", 5, "cafe_a", "【時間がかかるもの】二人分のカップに替え、何回か会ってやっと分かるという受けへ"),
        img("日本のデータでも", 6, "meeting_a", "【日本のデータ】面談用の小さなテーブルと椅子に替え、追跡研究の規模を出す",
            telop="男性825人・女性757人を約1年4か月追跡"),
        img("大手の結婚相談サービスに", 7, "chairs_a", "【研究の帰属】面談室の別カットに替え、実施した研究チームを示す",
            source="鈴木翔・須藤康介・寺田悠希・小黒恵 (2018)『理論と方法』33(2)"),
        img("お見合いを申し込まれた数で見ると", 8, "chairs_b", "【申し込まれた数】椅子の並ぶ会場に替え、人気と結びついた条件を並べる"),
        board("まだ半分よ",
              "【二つのものさし】申し込まれる段階と結ばれる段階で有利に働くものが食い違うことを黒板に書き、決め文の間2.0秒まで保持する",
              telop=OFFER_BOARD),
        img("人気なのに、結婚できてないのだ", 9, "meeting_c", "【言えるところまで】面談室の別カットに替え、研究が言える範囲を区切る"),
        img("直接の証明ではないけれど", 10, "watch_d", "【決め文の保持】時計の別カットに替え、有利に働き始めるのが遅いという決め文と間2.5秒を持たせる"),
        img("遅いなら、その時間は", 11, "cafe_window_b", "【次章への問い】カフェの窓際に替え、その時間はどこで手に入れるのかという問いで閉じる"),
    ],
    # ---------------- S9 その時間を、昔は誰が用意していたのか（歴史） ----------------
    9: [
        chapter(),
        img(None, 1, "phone_a", "【今から過去へ】夜のスマホの手元で受けてから、時代をさかのぼる合図にする"),
        img("明治より前の村では", 2, "wedding_b", "【家が決める結婚】古い和装の記念写真に替え、明治の民法の話に入る",
            telop="明治民法「戸主ノ同意」", source="明治民法 第750条／阪井裕一郎『仲人の近代』青弓社 2021"),
        img("本人の気持ちだけじゃ", 3, "venue_a", "【仲人が間に立った】結婚式場に替え、保証と段取りを担った役の説明へ"),
        img("慶應義塾大学の准教授", 4, "venue_b", "【近代の制度】式場の別カットに替え、見合い結婚が近代の制度だという研究を示す",
            source="阪井裕一郎『仲人の近代』青弓社 2021（慶應義塾大学 准教授）"),
        img("1947年、憲法に", 5, "wedding_b", "【本人が選ぶものへ】記念写真に戻し、憲法24条で結婚が本人のものになったことを出す",
            telop="憲法24条「両性の合意のみ」（1947年）", source="日本国憲法 第24条"),
        img("それでも仲人の慣行は", 6, "venue_a", "【7年でほぼ消えた】式場に替え、仲人を立てた割合の急落を数字で出す",
            telop="仲人を立てた割合 1994年63.9%→2001年7.3%",
            source="小関孝子 (2019) 社会デザイン学会学会誌 11（ゼクシィ結婚トレンド調査 2004）"),
        img("7年で、63パーセントから", 7, "venue_b", "【驚きの受け】式場の別カットに替え、ずんだもんの驚きで一拍置く"),
        img("1930年代に結婚した夫婦では", 8, "wedding_b", "【見合いの減少】記念写真に戻し、69.0%から9.9%への落差を出す",
            telop="見合い結婚 69.0% → 9.9%", source=IPSS),
        img("かわりにネットで出会った夫婦が", 9, "phone_c", "【ネットの増加】夜のスマホの手元に替え、ネットが見合いを追い抜いたことを出す",
            telop="ネットで出会う 15.2%"),
        diagram(
            "見合いと仲人には",
            "【誰が用意していたか】周りの人の保証と、何度も会う時間の二つが、見合いと仲人には先に付いていたことを収束で見せる。決め文で保持",
            {
                "type": "narrative",
                "layout": "converge",
                "items": [
                    {"id": "vouch", "text": "周りの人の保証", "at": "周りの人の保証と、何度も会う時間",
                     "after": "周りの人の保証"},
                    {"id": "time", "text": "何度も会う時間", "at": "周りの人の保証と、何度も会う時間",
                     "after": "何度も会う"},
                ],
                "result": {"text": "見合いと仲人", "at": "誠実さが有利に働き始めるまでの時間を",
                           "after": "他人が"},
            },
        ),
        img("今は、その保証も時間も", 10, "commute_d", "【自分で用意する時代】街を歩く人々に替え、今は保証も時間も自分持ちだという受けへ"),
        img("昔がよかった", 11, "venue_b", "【留保】式場に替え、昔がよかったという話ではないという断りを置く"),
        img("僕はずっと、会う前の段階で", 12, "cafe_c", "【章末の問い】カフェのカットに替え、結局何に負けているのかという問いで閉じる"),
    ],
    # ---------------- S10 結び（真のモテ要素とは何か） ----------------
    10: [
        img(None, 1, "commute_d", "【結びの整理】街を歩く人々の絵で、冒頭の一行に戻る"),
        board("会う前は、感じの良さまで", "【段階ごとの答え①】会う前は誠実さまで確認できない、を黒板に書く",
              telop=answer_board(1)),
        board("初対面は、見た目、人当たり", "【段階ごとの答え②】初対面で有利に働く三つを書き足す", telop=answer_board(2)),
        board("そして長い関係で", "【段階ごとの答え③】長い関係で有利になるものを書き足し、三段そろえる", telop=answer_board(3)),
        img("そう。", 2, "hands_c", "【遅いだけ】組んだ手に替え、誠実さは弱いのではなく遅いのだという整理へ"),
        img("誠実さが嫌われているから", 3, "group_g", "【決め文の保持】人が集まって声を合わせる場面に替え、判断が終わる場面が増えたという決め文と間2.5秒を持たせる"),
        img("自分の人格のせいにしなくていい", 4, "group_b", "【人格のせいにしない】人が輪になって同じ作業をする場面に替え、断りを添える"),
        img("誠実さは、持っているだけでは", 5, "group_g", "【決め文の保持】声を合わせる場面に戻し、伝わる場所まで行くという決め文と間2.5秒を持たせる"),
        img("プロフィールだけを書き直し", 6, "group_a", "【方針の転換】数人で紙を囲む場面に替え、書き直すのをやめると言うところまで"),
        img("書き直すより", 7, "group_d", "【自分の答え】資料を囲んで話す場面に替え、同じ人と何回か会える場所を探すという答えへ"),
        img("それは研究で確かめられた", 8, "group_b", "【留保】輪になる場面に戻し、研究で確かめられた方法ではないという断りを置く"),
        img("頑張って、ずんだもん", 9, "group_f", "【象徴的な最後の一枚】手仕事を教え合う場面で終え、間2.5秒とアウトロへつなぐ"),
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
                b["slot"] = img_i  # 画像ビートの通し番号（img() の slot 引数は無視する。板の抜き差しで番号がずれないように）
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
