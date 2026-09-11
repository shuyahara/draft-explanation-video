"""めたん×ずんだもん版・「なぜ"まとも"な男性はモテないのか」: ビート（貼り写真 / 章カード /
黒板文字 / チョーク図解）と追加 readings・pause_after を YAML に貼り直す。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（淫夢版・男女論版と同じ方式）。

  .venv\\Scripts\\python.exe scripts/20260911-matome-dansei-kamishibai/apply_beats.py

前提: tools/kamishibai_md_to_yaml.py で YAML（narration 部）を生成済み。生成コマンドは

  python tools/kamishibai_md_to_yaml.py <台本md> --v5-yaml <同フォルダの empty-v5-stub.yaml>
      --out <同名yaml> --bgm ../bgm/meisou-no-piano.mp3
      --bgm-credit "BGM:「瞑想のピアノ」lei（DOVA-SYNDROME）" --puppet-sink 0.12 --tempo 1.1

貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-matome/scene_NN_beat{slot}.*`
（配置は stage_assets.py）。

---------------------------------------------------------------------------
図解 11 箇所の型: 台本の指定と、ツールで描けるかの突合（2026-09-11）
---------------------------------------------------------------------------
台本「画面」欄の指定は S2 radiate / S3 sketch / S4 chain / S5 chart / S6 radiate / S7 row /
S9 sketch / S10 chain / S11 converge / S12 row / S13 converge。このうち **3 箇所は指定の型では
台本が描こうとしている絵にならない**ことが実装読みで分かったため、CLAUDE.md 図解の最上位規則
（「描ける型が無ければ、既存の型に説明を曲げて合わせない」）に従い `sketch` で描き直した
（2026-09-11 オーケストレーター承認済み）。ツール側への要望として切り出せるよう、描けなかった
理由を実装の該当箇所つきで残す。

■ sketch で代替した 3 箇所

  S7（台本 row → sketch 3行4列の数値表）
    narrative/row は `count` 個の同型ピクトグラムを横1列に並べ、`select.lit` で一部を点灯させる
    だけの型（`diagram.py: _compute_narrative_row_layout`。y は固定 0.39、x は等間隔、持てるのは
    icon と caption のみ）。台本が要求する「左列／右列の列見出し・各列3行・相関係数の数値」を
    表現する場はどこにも無い。sketch なら 1 列目に行見出し（威圧して従わせる／能力で尊敬される）、
    2〜4 列目に 好感度／短い関係／長い関係 の値を置けるので、左列3行目だけ符号が反転することが
    一目で分かる。

  S12（台本 row → sketch 3行2列）
    同上。台本の「ふつうの席順／入れ替えた席順の2列、各列に 移動する側 → 厳しく選ぶ側」は
    列見出し＋縦矢印が要る。sketch の `arrows`（縦）と `highlight` で「入れ替えたら結果も
    入れ替わる」を見せた。

  S6（台本 radiate → sketch 3行2列）
    narrative/radiate は「中心＝画面左・items＝画面右の縦並び」に固定（`_compute_narrative_radiate_layout`。
    cx=0.27・x_label=0.58）で、台本の「中心から**二方向**に伸びる」形は描けない。さらに決め文で
    「S2 の四つが全部『人に良くする力』の側に入る」ことを示したいが、`turn` は既出・未出を問わず
    **items 全体の色を変える**実装（`_draw_narrative_radiate_frame` の `color` が全 item 共有）
    なので「片側にだけ印」が作れない。sketch の2列（人に良くする力／自分から前に出る力）にし、
    左列に S2 の四つ、右列は「？」のまま残して caption「右の列に、入っているものがない」で
    決め文に同期させた。二本のものさしの説明自体は写真（笑い合う二人／ゆったり座って話す人）へ
    譲って図解の保持を約25秒に抑えている。

■ 型は変えず、描き方を寄せた 2 箇所

  S4 chain: 「上下を結ぶ矢印が**つながらない**ことを見せる」は、chain が隣接バンド間に必ず
    下向き矢印を引く実装（`_compute_narrative_chain_layout` の `arrows`）なので不可。下段を
    「実際に惹かれた相手」＋アイコン help（？）にし、caption「ここがつながらない」で示した。
  S10 chain: 「時間軸の二本の線と交差点」は折れ線グラフであって chain では描けない
    （`chart` は本編1箇所の上限を S5 が使用）。時系列の一本鎖
    「初対面＝前に出る力 → 何週間か後＝下がる → まともさは遅れて効く」に組み替え、
    caption「後半は推論」を台本どおり添えた。

■ S2 radiate は指定どおり
  ただし上記のとおり `turn` が使えないので、ラベル自体に「＝減点なし」×3／「＝相手へ」を入れて
  非対称を見せている（`turn` は書いていない）。

■ 型の重複について
  結果として sketch は S3・S6・S7・S9・S12 の 5 回で、「同一の型は1本につき2回まで」「隣接する
  図解ビートに同じ layout を使わない」（S6→S7、S7→S9。S8 に図解が無いため隣接）を外れる。
  最上位規則を優先するというユーザー判断（2026-09-11）に基づく。格子の形は
  S3=2行3列の流れ図／S6=3行2列の対比／S7=3行4列の数値表／S9=2行3列の分岐／S12=3行2列＋縦矢印
  と互いに変えてある。

■ ツール側の制約メモ（台本を曲げないために踏んだ回避策）
  - sketch は **行3・列4 が上限**。S6 の「左列に四つを1セルずつ」は4行必要なので描けず、
    「犯罪・浮気をしない」「働いている・優しい」の2セルに畳んだ（語は台本のまま）。
  - chart の値ラベルは **小数1桁に丸められる**（`_format_chart_value`）。S5 は 0.43/0.29/0.19 が
    0.4/0.3/0.2 と出てしまうため、項目ラベル側に値を入れた（「見た目0.43」等。label は8文字以内）。
    棒の上のツール側ラベル（0.4 等）と**二重表示**になる。
  - narrative/converge はラベルが9文字以上あると自動縮小率が 0.6 を割る（S13 で 0.48 の警告）。
    四点の要約は全ラベル8文字以内にして 0.66 に収めた。
  - 1行 telop（image ビート）は **自動縮小されない**（`render_telop_layer` の1行経路は
    TELOP_FONT_RATIO 固定）。黒板幅の 92%（1920x1080 で約 1663px ＝ 全角約27字）を超えると
    左右が切れる。preflight の 30 字規約とあわせ、telop は数値・要点だけにして、**研究の出典
    （著者・年・誌名）は `credit`（字幕帯右下の小文字）へ移した**（`img(..., source=...)`）。
  - ビート境界は**キュー境界にしか置けない**ので、S6 の「開いた姿勢 → 縮こまった姿勢」の切り替え
    （同一キュー内の対比）は、次のキュー（ずんだもんの「姿勢だけで！？」）で行っている。

図解の保持は目安40秒に収まるよう前振りを image ビートへ譲った。意図的に残した例外は
S13（約78秒。シーン全体が四点のまとめで、貼り写真なしの指定。converge が要素を1つずつ足す）と
S12（約51秒。2列の対比を決め文2つまで保持する）。

黒板文字（board）は台本指定どおり S2（三つの段階）と S14（段階ごとの答え）の2箇所だけ。
S14 は「段階ごとに分けて出す」指定なので、ナレーションの順（会ったあと→続いてから→会う前）に
行を足していく3枚に分けた（最後の1枚が見出し込み4行）。

貼り写真は candidates-matome/manifest-s01-s07.md・manifest-s08-s14.md の **推奨** をそのまま採用。
S6 の「縮こまった姿勢」は台詞の途中（同一キュー内）では切り替えられないため、ずんだもんの
「姿勢だけで！？」のキューで対比の1枚に切り替えている。
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

YAML_PATH = Path(__file__).with_name("20260911-matome-dansei-kamishibai.yaml")

# 出典表記（貼り写真の下＝字幕帯の右下）。candidates-matome の manifest から転記。
# 2026-09-11 レンダ v1 のフレーム点検・GPT 映像レビューを受けて、**同じ写真の使い回しを減らすため
# 候補の b/c/d も採る**ようにした（同一ファイルは原則1シーン内に閉じる。シーンをまたぐのは、
# 意味のある回収だけ: 夜のスマホ＝会う前／組んだ手＝S8のデート／会場の椅子＝同じ実験）。
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
    "respect_c": "Photo: Pexels",
    "cafe_window_a": "Photo: Sare / Pexels",
    "cafe_window_b": "Photo: Sare / Pexels",
    "cafe_window_c": "Photo: dilay (:) / Pexels",
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
    "respect_c": "stock/s07_respect_c.jpg",
    "cafe_window_a": "stock/s08_cafe_window_a.jpg",
    "cafe_window_b": "stock/s08_cafe_window_b.jpg",
    "cafe_window_c": "stock/s08_cafe_window_c.jpg",
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
}

# 台本「発音・ポーズメモ」の読み。**登録は最小限**にする（VOICEVOX が正しく読む語を登録すると
# 複合語の読みが壊れる。memory/voicevox-user-dict-priority.md）。ここに入れていない語
# （人格・威圧・見合い・見立て・威張る・別々・協調性・誠実性・准教授・小数点の数値など）は
# preflight の読み突合で確認する。
GLOBAL_READINGS = [
    ("博士課程", "ハクシカテイ"),
    ("奥手", "オクテ"),
    ("人柄", "ヒトガラ"),
    # 2026-09-11 の VOICEVOX 突合（preflight-readings.md §1）で実際に誤読した語。
    # 助詞「は」は辞書の読みに書くと「ハ」と発音されてしまうため、surface は助詞を外した最小形に
    # している（「いちばん上は」→「いちばん上」、「やり方は」→「やり方」、「筋は通っている」→
    # 「通っている」）。読みはどの出現でも同じなので、複合語を壊す心配はない。
    ("顔がいい方", "カオガイイホウ"),
    ("いちばん上", "イチバンウエ"),
    ("どんな人か", "ドンナヒトカ"),
    ("変な人", "ヘンナヒト"),
    ("やり方", "ヤリカタ"),
    ("通っている", "トオッテイル"),
    ("18歳", "ジュウハッサイ"),
    ("34歳", "サンジュウヨンサイ"),
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 間レビュー前の一次反映: 台本「発音・ポーズメモ」「演出」のうち（間 N）で明示済みでないもの
# （生成側の既定値＝話者交代0.45・文境界0.35・章末1.2 から動かす箇所だけ）。
# pause_after はセグメント末尾に効くので、セグメント末尾の一文で照合する。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [("損をするのだ", 0.9), ("本当にモテないのか", 0.6)],
    2: [("この三つで、効くものが違うの", 0.6)],
    3: [("顔がいい方が負けたのだ", 0.6)],
    4: [("ほとんど、当たらなかったわ", 0.8)],
    8: [("自分からは、何か切り出した", 0.6), ("分かる材料は、あったかしら", 0.6), ("1回で伝わるのは、そこまでね", 1.2)],
    11: [("共通していたものが二つあるのよ", 0.6)],
    13: [("ここまでを、四つにまとめるわね", 0.45)],
    14: [("関係が始まったあとで、ね", 0.6)],
}


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


BEATS = {
    # ---------------- S1 フック（半年でマッチ3件） ----------------
    1: [
        img(None, 1, "phone_c", "【半年の書き直し】夜の部屋でスマホを見る手元から始める"),
        img("それで、成立したマッチは", 2, "phone_c",
            "【数字】同じ手元のまま、マッチ3件の数字を台詞と同時にテロップで出す",
            telop="半年でマッチ3件"),
        img("しかも、実際に会えたのは", 3, "cafe_a",
            "【会ったあとで止まった1件】二人分のカップに替え、会えた1人の話へ",
            telop="会えたのは1人"),
        img("僕、そんなに変なことは", 4, "phone_a", "【プロフィールへ戻る】書いた内容の話に戻るので手元カットへ"),
        img("掲示板で", 5, "bbs_board", "【掲示板の書き込み】「まともな男ほどモテない」を見た画面（文字は描かない）"),
        img("それを、一緒に確かめましょう", 6, "phone_a", "【問いの言語化】本人の状況に戻し、この動画が答える問いを立てる"),
        img("先に、答えの形だけ", 7, "cafe_c", "【答えの形の予告】カフェのカットで「嫌われてはいない／選ばれにくい」を予告"),
        img("嫌われてはいない", 8, "phone_c", "【間】手元に戻り、ずんだもんが違いを飲み込めないところまで尺を分ける"),
    ],
    # ---------------- S2 「まとも」の中身を、ほどく ----------------
    2: [
        img(None, 1, "commute_e", "【当たり前の暮らし】通勤する人たちの後ろ姿で「まとも」の中身をほどく前振り"),
        img("えっと…犯罪はしてないのだ", 2, "commute_e", "【四つの列挙】同じ絵のまま、ずんだもんが四つを数え上げるところまで尺を分ける"),
        diagram(
            "犯罪をしない。",
            "【四つの内訳】めたんの言い直しに合わせて四つを1つずつ黒板に出し、三つが「減点なし」・四つ目だけが相手へ向かうことを見せる",
            {
                "type": "narrative",
                "layout": "radiate",
                "center": {"icon": "person", "text": "まとも", "at": "犯罪をしない。"},
                "items": [
                    {"id": "crime", "text": "犯罪をしない＝減点なし", "at": "犯罪をしない。"},
                    {"id": "affair", "text": "浮気をしない＝減点なし", "at": "浮気をしない。"},
                    {"id": "work", "text": "働いている＝減点なし", "at": "働いている。"},
                    {"id": "kind", "text": "優しい＝相手へ", "at": "優しい。"},
                ],
            },
        ),
        img("そしてこれは、ずんだもん一人の話ではないわ", 3, "commute_e", "【個人の話から数字へ】通勤の絵に戻し、調査の数字へ移る"),
        img("2021年に行った調査があるの", 4, "commute_e",
            "【72.2%】交際相手がいない割合を数字と同時に出す",
            telop="交際相手なし 72.2%（18〜34歳 未婚男性）"),
        img("同じ調査で、結婚するつもりが", 5, "commute_c",
            "【43.3%】独身でいる理由の1位を出す",
            telop="「適当な相手にめぐり会わない」43.3%"),
        img("つまり、自分に合う相手と", 6, "commute_c",
            "【言い換え】自分に合う相手と出会っていない、という言い換えまで尺を分ける",
            source="国立社会保障・人口問題研究所 第16回出生動向基本調査（2021年）"),
        img("ただ、この調査はその人が", 7, "commute_c", "【留保と段階分けの前置き】この調査が測っていないことと、段階を分ける宣言へ"),
        board("写真とプロフィールしか見えていない、会う前。",
              "【全編の骨格】三つの段階を黒板に書き、以後のシーンで参照できるようにする",
              telop="三つの段階\n①会う前＝写真とプロフィール\n②会ったあと＝初対面〜数回\n③続いてから＝関係が始まった後"),
        img("僕は、会う前でも", 8, "commute_c", "【次章への問い】通勤の絵に戻し、優しさが嫌われているのかという問いで閉じる"),
    ],
    # ---------------- S3 「優しい男は損をする」は、本当なのか ----------------
    3: [
        chapter(),
        img(None, 1, "university_b", "【実験の紹介】大学の校舎で2003年の実験に入る。図解の前振りとして短く",
            source="Urbaniak & Kilmann (2003) Sex Roles 49(9/10)"),
        diagram(
            "二人の男性を、写真と紹介文で見せるの",
            "【実験の骨格】二人の男性→女子学生に聞いた→感じがいい方が選ばれた、を格子で見せる",
            sketch(
                [
                    [
                        cell("mean_man", icon="person", text="見た目◎ 意地悪", at="一人は見た目の評価が高いけれど"),
                        cell("ask", icon="forum", text="女子学生に聞いた", at="どちらがいいか、と聞いたの"),
                        cell("chosen", icon="thumb_up", text="感じがいい方が選ばれた", at="選ばれたのは、感じがいい方だったの"),
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
        img("この実験は二度行われていて", 2, "university_c", "【再現性】別の校舎の絵に替え、二度の実験と人数を出す",
            telop="二度の実験 N=48／N=194（2003年）"),
        img("でも、見た目と態度の両方が違うのだ", 3, "facetoface_b", "【交絡への疑問】向かい合って話す二人の写真に替え、優しさだけの力かという疑問を受ける"),
        img("この実験では、見た目の良さと態度の良さが", 4, "facetoface_b", "【決め文の保持】同じ絵のまま、負けていたのは意地悪な態度だという決め文と間2.0秒を持たせる"),
        img("じゃあ「優しい男は損をする」っていうのは", 5, "university_b", "【俗説そのものへ】校舎に戻り、俗説を扱った別の研究へ移る"),
        img("カナダのゲルフ大学", 6, "university_c", "【1999年の研究】ゲルフ大学の設問を紹介する",
            source="Herold & Milhausen (1999) J Sex Marital Ther 25(4)"),
        img("3倍じゃないか", 7, "facetoface_b", "【数字の受け】向かい合って話す二人に戻り、54%対18%の驚きを受ける",
            telop="優しい方 54%・魅力的な方 18%（1999年）"),
        img("ただし、こちらは優しさ以外も", 8, "facetoface_b", "【限定】同じ絵のまま、この数字を優しさの力とは読めない旨と章末の問いへ"),
    ],
    # ---------------- S4 人は、誰に惹かれるか分かっているのか ----------------
    4: [
        chapter(),
        img(None, 1, "phone_c", "【会う前の段階】夜のスマホの手元で、会う前は写真とプロフィールしか見えないことを示す（映像レビュー①: 通勤写真では会う前の段階に見えない）"),
        img("いちばん多かったのは「人柄」よ", 2, "phone_c", "【人柄88.2%】重視すると答えた割合を出す",
            telop="人柄を重視 88.2%／容姿 18.8%（女性・2021年）"),
        img("2008年、ノースウェスタン大学", 3, "facetoface_a", "【実験へ】向かい合う二人の席に替え、スピードデートの実験に入る",
            source="Eastwick & Finkel (2008) JPSP 94(2)"),
        img("そのあと、一人4分ずつ", 4, "facetoface_a", "【4分ずつ】同じ絵のまま、実験の手順と人数を出す",
            telop="163人／一人4分ずつ 9〜13人と"),
        img("ほとんど当たらなかったのだ？", 5, "chairs_c", "【当たらなかった】スピードデートの会場に替え、ずんだもんの驚きから確かさの説明へ"),
        img("事前に挙げた理想に合う人ほど", 6, "chairs_c", "【メタ分析】97本をまとめた分析でも同じだったことを出す",
            telop="97本の研究をまとめた分析（2014年）", source="Eastwick et al. (2014) Psychol Bull 140(3)"),
        img("あの88.2パーセントは嘘なのだ", 7, "facetoface_a", "【問い返し】向かい合う二人に戻り、答えた理想は嘘なのかという問いを受ける（図解の保持を短くするための前振り）"),
        diagram(
            "嘘とは言えないわ",
            "【つながらない上下】会う前に答えた理想と、会ったあと実際に惹かれた相手を上下に置き、下段は？のまま結びつかないことだけを見せる",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "ideal", "text": "答えた理想＝人柄", "icon": "edit", "at": "嘘とは言えないわ"},
                    {"id": "real", "text": "実際に惹かれた相手", "icon": "help", "at": "ただ、本人の答えだけでは"},
                ],
                "caption": {"text": "ここがつながらない", "at": "聞かれると、理由をあとから", "after": "聞かれると、理由をあとから"},
            },
        ),
    ],
    # ---------------- S5 では、実際には何が効いていたのか ----------------
    5: [
        img(None, 1, "chairs_c", "【同じ実験の続き】スピードデートの会場の絵のまま、4分の会話で何が効いたかに入る"),
        img("やっぱり顔なのだ", 2, "chairs_c", "【順位への落胆】同じ絵のまま、いちばん上は変わらないという受けから数字の開きの話へ尺を分ける"),
        diagram(
            "見た目は0.43から0.46",
            "【相関の大きさ】数字の開きそのものが主張なので棒グラフにする。人当たりの棒が稼ぐ力より明らかに長いことを見せる",
            {
                "type": "chart",
                "chart": "bar",
                "title": "恋愛的関心との相関（男性の場合。女性でも順番は同じ）",
                "source": "Eastwick & Finkel (2008) JPSP 94(2)",
                "series": [
                    {
                        "color": "accent",
                        "at": "見た目は0.43から0.46",
                        "points": [
                            {"label": "見た目0.43", "value": 0.43},
                            {"label": "人当たり0.29", "value": 0.29},
                            {"label": "稼ぐ力0.19", "value": 0.19},
                        ],
                    }
                ],
            },
        ),
        img("報われるのだ", 2, "laughing_a", "【人当たりの良さ】笑いながら会話している二人に替え、言葉の意味の限定へ"),
        img("「優しい」と全部同じじゃないのだ", 3, "laughing_a", "【次章への問い】同じ絵のまま、最初の4分で何を落としているのかという問いへ"),
    ],
    # ---------------- S6 優しさの隣に、何が足りないのか ----------------
    6: [
        chapter(),
        img(None, 1, "open_a", "【いちばん大事なところ】くつろいで話す人の絵で章に入り、二本のものさしの説明へ渡す"),
        img("人の魅力は、二つのものさしで", 2, "open_a",
            "【人に良くする力】同じ絵のまま、一本目のものさし（優しさ・誠実さ・思いやり）の説明へ尺を分ける"),
        img("もう一つは、自分から前に出る力", 3, "open_c",
            "【自分から前に出る力】ゆったり座って話す人に替え、二本目のものさし（姿勢や発言で見せる）を直接描く"),
        img("そこが、いちばん勘違いされやすいところね", 4, "open_a", "【反対ではない】同じ絵に戻し、二つが別々のものさしである話を続ける"),
        img("だから「優しさを捨てて男らしくなれ」", 5, "open_b", "【誤解を断つ】身振りを交えて話す人に替え、優しさを減らしても自信は上がらない話へ"),
        img("断っておくと、この二つで人の魅力が", 6, "open_b", "【範囲の限定】同じ絵のまま、二本で全部が説明できるわけではない旨まで尺を分ける"),
        diagram(
            "そのうえで、さっきずんだもんが挙げた四つを",
            "【四つはどちらの列か】二本のものさしを列見出しにして、S2の四つが全部左の列に入り、右の列が空のままであることを見せる。決め文「一つも入っていないわ」で保持（S7 の sketch と隣接するが、こちらは2列×3行の対比、S7 は3行4列の数値表で格子の形が違う）",
            sketch(
                [
                    [
                        cell("kind_h", icon="volunteer_activism", text="人に良くする力", at="そのうえで、さっきずんだもんが挙げた四つを"),
                        cell("front_h", icon="campaign", text="自分から前に出る力", at="そのうえで、さっきずんだもんが挙げた四つを"),
                    ],
                    [
                        cell("kind_1", text="犯罪・浮気をしない", at="犯罪をしない、浮気をしない", after="犯罪をしない、浮気をしない"),
                        cell("front_q", text="？", at="そのうえで、さっきずんだもんが挙げた四つを"),
                    ],
                    [
                        cell("kind_2", text="働いている・優しい", at="犯罪をしない、浮気をしない", after="働いてる"),
                        None,
                    ],
                ],
                highlight={"ids": ["front_q"], "at": "自分から前に出る力は", "after": "自分から前に出る力は"},
                caption={"text": "右の列に、入っているものがない", "at": "四つとも、問題を起こさないか",
                         "after": "四つとも、問題を起こさないか"},
            ),
        ),
        img("だから、「まとも」だと言えるだけでは", 7, "closed_b", "【間】縮こまった姿勢の別カットに替え、まともさだけでは伝わらないという受けまで尺を分ける"),
        img("その前に出る力が実際に効くことも", 8, "open_b", "【姿勢の研究へ】バークレー校の研究の紹介に入る",
            source="Vacharkulksemsuk et al. (2016) PNAS 113(15)"),
        img("体を開いて、ゆったりした姿勢", 9, "open_c", "【開いた姿勢】体を開いた姿勢の写真に戻り、1.76倍の結果を出す",
            telop="開いた姿勢 約1.76倍／アプリ 約1.27倍"),
        img("姿勢だけで！？", 10, "closed_a", "【対比の1枚】比較対象の縮こまった姿勢に切り替える（同じ1枚に入れず image ビートを分ける指定。台詞の途中では切れないので、ずんだもんの驚きのキューで切り替えた）"),
        img("ただし、姿勢が伝えていたのが余裕だけ", 11, "open_c", "【留保】開いた姿勢に戻し、姿勢が伝えていたものの限定と早合点へ"),
    ],
    # ---------------- S7 男らしさには、二種類ある ----------------
    7: [
        img(None, 1, "intimidate_c", "【二種類ある】会議室で腕を組む人の写真で、高い位置に立つ二つのやり方に入る",
            source="Cheng et al. (2013) JPSP 104(1), Study 1（仲間評定）"),
        img("一つ目は、相手を威圧して従わせるやり方", 2, "intimidate_c", "【威圧して従わせる】同じ絵のまま、怖がらせて従わせる説明に尺を分ける"),
        img("二つ目は、能力で尊敬されるやり方", 3, "respect_a", "【能力で尊敬される】人が集まって話を聞いている場面に替え、もう一方のやり方を見せる"),
        img("それが、ほとんど関係がなかったの", 4, "respect_a", "【0.01】二つがほぼ無関係であることを数字で出す",
            telop="二つの結びつき 0.01（別の力）"),
        img("そして、好かれ方がまるで違うのよ", 5, "respect_b", "【好感度】聞き入る人たちの別カットに替え、好かれているのは尊敬される方だという決め文と間2.0秒を持たせる",
            telop="尊敬される力 +0.73・威圧する力 マイナス0.06"),
        img("でも、怖い人がモテてるのは", 6, "intimidate_a", "【怖い人がモテる】腕を組む人の別カットに替え、短期を求める人を調べた研究へ渡す（図解の保持を短くするための前振り）",
            source="Witkower & Rule (2025) SPPS 17(5), Study 1"),
        diagram(
            "短い関係を探している人ほど",
            "【符号の反転】二つのやり方×三つの相手で数値表を作り、威圧する力だけが長い関係で符号を反転させることを見せる",
            sketch(
                [
                    [
                        None,
                        cell("h_like", text="好感度", at="短い関係を探している人ほど"),
                        cell("h_short", text="短い関係を探す人", at="短い関係を探している人ほど"),
                        cell("h_long", text="長く続く関係の人", at="短い関係を探している人ほど"),
                    ],
                    [
                        cell("dom", icon="gavel", text="威圧して従わせる", at="短い関係を探している人ほど"),
                        cell("dom_like", value="マイナス0.06", at="短い関係を探している人ほど"),
                        cell("dom_short", value="+0.58", at="数字は0.58"),
                        cell("dom_long", value="マイナス0.55", at="ところが、長く続く関係を探している人では",
                             after="ところが、長く続く関係を探している人では"),
                    ],
                    [
                        cell("pre", icon="military_tech", text="能力で尊敬される", at="短い関係を探している人ほど"),
                        cell("pre_like", value="+0.73", at="短い関係を探している人ほど"),
                        cell("pre_short", value="+0.16", at="いっぽう、尊敬されるやり方は", after="短くても長くても"),
                        cell("pre_long", value="+0.15", at="いっぽう、尊敬されるやり方は", after="短くても長くても"),
                    ],
                ],
                highlight={"ids": ["dom_long"], "at": "威圧して従わせるやり方と", "after": "威圧して従わせるやり方と"},
                caption={"text": "仲間評定。マイナス0.06は有意差なし", "at": "短い関係を探している人ほど"},
            ),
        ),
        img("ここで言う「モテてる」は", 7, "respect_c", "【言い分けの確認】聞いている場面の別カットに替え、モテの種類を分けた受けを見せる"),
        img("もう一つ断っておくわね", 8, "respect_c", "【範囲の限定】同じ絵のまま、男らしさを二分した研究ではない旨と、次章への嫌な予感へ"),
    ],
    # ---------------- S8 僕の1回は、何だったのか（章カードなし・図解なし） ----------------
    8: [
        img(None, 1, "cafe_window_a", "【研究から離れる】カフェの窓際の席で、ずんだもんの1回のデートの話に入る"),
        img("何を話したの", 2, "cafe_window_a", "【聞き役に徹した1時間】同じ絵のまま、何を話したかを聞く"),
        img("自分からは、何か切り出した", 3, "cafe_window_b", "【自分からは切り出したか】窓際の別カットに替え、めたんの問いまで尺を分ける"),
        img("失礼があったら困るから", 4, "hands_a", "【待っていた手】テーブルの上で組んだ手に替え、聞かれるまで待っていた場面を見せる"),
        img("失礼がなかった、というのは", 5, "hands_a", "【減点がなかっただけ】同じ絵のまま、どんな人か分かる材料があったかへ"),
        img("僕、まじめに聞いてただけなのだ", 6, "hands_c", "【材料がない】組んだ手の別カットに替え、1回で伝わるのはそこまでという受けへ"),
        img("僕は「変な人じゃない」までは", 7, "cafe_window_c", "【本人の言語化】カフェの別カットに替え、伝わったこと・伝わらなかったことの整理へ"),
        img("でも、2回目に進めてる人って", 8, "cafe_window_c", "【次章への問い】同じ絵のまま、モテと結婚の関係を問う章末へ"),
    ],
    # ---------------- S9 モテることと、結ばれることは同じか ----------------
    9: [
        chapter(),
        img(None, 1, "meeting_a", "【日本のデータ】面談用の小さなテーブルと椅子で、結婚相談サービスの追跡研究に入る"),
        img("男性825人、女性757人", 2, "meeting_a", "【規模】人数と追跡期間、実施した研究チームを出す",
            telop="男性825人・女性757人を約1年4か月追跡"),
        diagram(
            "そこで、二つのものさしを分けて測ったの",
            "【二つのものさし】同じ825人を申し込まれた数と結婚成立の二つで測ると、効く条件が食い違うことを見せる",
            sketch(
                [
                    [
                        cell("men", icon="groups", text="同じ825人の男性", at="そこで、二つのものさしを分けて測ったの"),
                        cell("offers", icon="forum", text="申し込まれた数", at="お見合いを申し込まれた数と",
                             after="お見合いを申し込まれた数"),
                        cell("offers_res", text="学歴・収入・身長・体型", at="学歴が高いこと、収入が高いこと"),
                    ],
                    [
                        None,
                        cell("married", icon="favorite", text="結婚まで行ったか", at="お見合いを申し込まれた数と",
                             after="実際に結婚まで行ったかどうかよ"),
                        cell("married_res", text="収入以外は効かない", at="結婚まで行ったかどうかで見ると",
                             after="学歴も、身長も、体型も"),
                    ],
                ],
                arrows=[("men", "offers"), ("men", "married"), ("offers", "offers_res"), ("married", "married_res")],
                highlight={"ids": ["married_res"], "at": "例外は、収入の高さだけよ"},
            ),
        ),
        img("人気なのに、結婚できてないのだ", 3, "meeting_b", "【食い違いの受け】面談室の別カットに替え、一致していなかったという言い直しへ"),
        img("この研究では、理由も分析されているわ", 4, "meeting_b", "【理由】条件のいい人ほど相手を厳しく選ぶという分析を示す",
            source="鈴木翔・須藤康介・寺田悠希・小黒恵 (2018)『理論と方法』33(2)"),
        img("選ばれる側になると", 5, "meeting_c", "【決め文の保持】面談室の別カットに替え、モテることと結ばれることは別のものさしだという決め文と間2.0秒を持たせる"),
    ],
    # ---------------- S10 遅れて効いてくるもの ----------------
    10: [
        img(None, 1, "laughing_d", "【続いてからの段階】笑い合う二人の絵で、関係が始まったあとの話に入る",
            telop="19の調査・3,848人をまとめた分析", source="Malouff, Schutte, Bhullar et al. (2010) J Res Pers 44(1)"),
        img("2010年、オーストラリアの", 2, "laughing_d", "【研究の帰属】ニューイングランド大学の准教授の仕事だと示す",
            telop="協調性・誠実性・感情の安定と満足度 0.25〜0.29"),
        img("協調性の高さ。", 3, "laughing_d", "【三つの性質】同じ絵のまま、満足度と結びついていた三つと数字を出す"),
        img("数字は0.25から0.29", 4, "laughing_d", "【自分の持ち物】同じ絵のまま、ずんだもんが持っている性質だという受けへ"),
        img("だから、まともさが弱いわけでは", 4, "watch_d", "【測っていないこと】待ち合わせで時計を見る人に替え、この研究が測っていない範囲の限定と間1.5秒を持たせる"),
        img("ここからは、研究そのものではなく", 5, "hands_a", "【推論の宣言】S8のデートで組んでいた手に戻し、ここからは推論だと断る（約束を守る人かどうかは4分では分からない、の回収）"),
        img("分からないのだ…", 6, "watch_a", "【時間がかかるもの】待ち合わせで時計を見る人に替え、何回か会ってやっと分かるという受けへ"),
        diagram(
            "いっぽう、自分から前に出る力の方は",
            "【効き始めの遅さ】初対面→何週間か後→まともさが効き始める、の順で並べ、後半は推論だとキャプションで明示する",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "first", "text": "初対面＝前に出る力", "icon": "visibility",
                     "at": "いっぽう、自分から前に出る力の方は"},
                    {"id": "weeks", "text": "何週間か後＝下がる", "icon": "trending_down",
                     "at": "自信たっぷりに見える人への高い評価は", "after": "自信たっぷりに見える人への高い評価は"},
                    {"id": "later", "text": "まともさは遅れて効く", "icon": "schedule",
                     "at": "まともさが弱いんじゃないのよ", "after": "まともさが弱い"},
                ],
                "caption": {"text": "後半は推論", "at": "いっぽう、自分から前に出る力の方は"},
            },
        ),
    ],
    # ---------------- S11 その「時間」は、誰が用意していたのか ----------------
    11: [
        chapter(),
        img(None, 1, "wedding_b", "【出会い方の変化】昔の記念写真で、夫婦の出会い方を年ごとに聞いた調査に入る",
            source="国立社会保障・人口問題研究所 第16回出生動向基本調査（2021年）図表5-2・5-3"),
        img("1930年代に結婚した夫婦では", 2, "wedding_b", "【見合いの減少】69.0%から9.9%への落差を数字で出す",
            telop="見合い結婚 69.0% → 9.9%"),
        img("職場で出会って結婚した割合も", 3, "office_a", "【職場の減少】オフィスで並んで働く人たちに替え、職場での出会いの減少を出す",
            telop="職場で出会う 28.2% → 21.4%"),
        img("そのかわりに増えたのが", 4, "phone_c", "【ネットの増加】夜のスマホの手元に替え、ネットでの出会いが見合いを追い抜いたことを出す（映像レビュー②: 職場の写真のままだと職場の出会いに見える）",
            telop="ネットで出会う 15.2%"),
        img("数はそうかもしれないわ", 5, "wedding_b", "【共通していた二つ】記念写真に戻し、見合いと職場に共通していた一つ目を言うところまで（図解の保持を短くするための前振り）"),
        diagram(
            "「この人はちゃんとした人ですよ」",
            "【誰が用意していたか】周りの人の保証と、先に決まっている何度も会う時間の二つが、昔は先に用意されていたことを収束で見せる",
            {
                "type": "narrative",
                "layout": "converge",
                "items": [
                    {"id": "vouch", "text": "周りの人の保証", "at": "「この人はちゃんとした人ですよ」"},
                    {"id": "time", "text": "何度も会う時間", "at": "もう一つは、何度も会う時間が"},
                ],
                "result": {"text": "昔は先に決まっていた", "at": "昔は、まともさを他人が保証してくれて",
                           "after": "しかも何度も会う時間が"},
            },
        ),
        img("減った分は、今は誰がやってるのだ", 6, "office_b", "【次章への問い】図解を留保の終わりまで保持したあと、オフィスの絵に替えて「減った分は今は誰がやっているのか」という問いへ（映像レビュー③: 留保の途中で1930年代の婚礼写真に戻さない）"),
    ],
    # ---------------- S12 近づく役を、誰がやっているか ----------------
    12: [
        img(None, 1, "phone_c", "【自分でやるしかない】夜のスマホの手元に戻り、近づく役の偏りを数字で見る",
            source="Kreager, Cavanagh, Yen & Yu (2014) J Marriage Fam 76(2)"),
        img("その半年で送られた最初のメッセージは", 2, "phone_c", "【4対1】最初のメッセージの件数の偏りを出す",
            telop="最初のメッセージ 男性142,444件・女性34,960件"),
        img("返事をもらえた割合も見てみましょう", 3, "phone_c", "【返信率は逆】送っている数と返る割合が男女で逆であることを出す",
            telop="未返信率 男性発79%・女性発58%"),
        img("そこまでは言えないの", 4, "phone_c", "【読みすぎない】同じ絵のまま、この数字から言えるところまでの限定へ"),
        img("そこで、その「近づく役」そのものを", 5, "chairs_a", "【席の実験へ】向かい合わせに並んだ椅子に替え、役を入れ替えた実験に入る",
            source="Finkel & Eastwick (2009) Psychol Sci 20(10)"),
        diagram(
            "ふつうは、男性が席を移動して",
            "【席順と結果】ふつうの席順と入れ替えた席順を左右に置き、移動する役を入れ替えると結果も入れ替わることを見せる",
            sketch(
                [
                    [
                        cell("norm_h", icon="event_seat", text="ふつうの席順", at="ふつうは、男性が席を移動して"),
                        cell("swap_h", icon="swap_horiz", text="入れ替えた席順", at="それを逆にして"),
                    ],
                    [
                        cell("norm_m", text="男性が移動する", at="ふつうは、男性が席を移動して", after="男性が席を移動して"),
                        cell("swap_m", text="女性が移動する", at="それを逆にして", after="それを逆にして"),
                    ],
                    [
                        cell("norm_r", text="厳しく選ぶのは女性", at="すると、ふだんのスピードデートで",
                             after="ふだんのスピードデートで見られる"),
                        cell("swap_r", text="厳しく選ぶのは男性", at="移動する側は相手を受け入れやすくなって",
                             after="移動する側は相手を受け入れやすくなって"),
                    ],
                ],
                arrows=[("norm_m", "norm_r"), ("swap_m", "swap_r")],
                highlight={"ids": ["swap_r"], "at": "座って待つ役をやっている側が", "after": "座って待つ役をやっている側が"},
                caption={"text": "入れ替えたら結果も入れ替わる", "at": "選り好みしているのが女性だから"},
            ),
        ),
        img("僕はずっと、送る側で", 6, "chairs_a", "【自分の役】椅子の絵のまま、ずっと送る側・移動する側だったという受けへ"),
        img("自分から近づく役、という点が共通している", 7, "phone_c", "【限定と次への問い】手元の絵に戻し、席の移動とメッセージは同じ行動ではない旨と章末の問いへ"),
    ],
    # ---------------- S13 まともな男性は、何に負けているのか ----------------
    13: [
        diagram(
            None,
            "【四点の収束】シーン全体が四つのまとめなので、四本を1つずつ黒板に足していき、決め文で中心へ収束させる（貼り写真なしの指定）",
            {
                "type": "narrative",
                "layout": "converge",
                "items": [
                    {"id": "one", "text": "優しさは負けない", "at": "一つ目。"},
                    {"id": "two", "text": "前に出る力がない", "at": "二つ目。"},
                    {"id": "three", "text": "好かれるのは尊敬", "at": "三つ目。"},
                    {"id": "four", "text": "出会い方が減った", "at": "四つ目。"},
                ],
                "result": {"text": "伝わる前に判断が終わる", "at": "まともさが伝わる前に",
                           "after": "まともさが伝わる前に"},
            },
        ),
        img("伝わる前に、終わってるのだ", 1, "phone_a", "【本人に戻る】図解を閉じ、夜のスマホの手元でずんだもんの「どうしたらいいのだ」へ渡す"),
    ],
    # ---------------- S14 結び（真のモテ要素とは何か） ----------------
    14: [
        img(None, 1, "group_g", "【結びの前置き】声を合わせる人たちの絵で、必ずうまくいく話ではないという断りから入る"),
        img("最初に決めた三つの段階ごとに", 2, "group_g", "【段階ごとに答える】同じ絵のまま、三つの段階に分けて答える宣言へ"),
        board("まず、会ったあと。",
              "【会ったあとの答え】実際に人が惹かれていた三つを黒板に書く",
              telop="段階ごとの答え\n②会ったあと＝見た目・人当たり・尊敬"),
        img("尊敬される強さの方は", 3, "respect_b", "【尊敬される方】一人の話に聞き入る人たちの絵に替え、威圧する方との違いを確認する"),
        board("次に、続いてから。",
              "【続いてからの答え】協調性・誠実性・感情の安定を書き足す",
              telop="段階ごとの答え\n②会ったあと＝見た目・人当たり・尊敬\n③続いてから＝協調性・誠実性・感情の安定"),
        img("そして、会う前。", 4, "phone_a", "【会う前がいちばん薄い】夜のスマホの手元に替え、写真と文字からは読み取れない話へ"),
        board("繰り返し会って相手を知る機会が",
              "【会う前の答え】三段そろえて、会う前がいちばん薄いことを書き足す",
              telop="段階ごとの答え\n①会う前＝写真と文字からは読み取れない\n②会ったあと＝見た目・人当たり・尊敬\n③続いてから＝協調性・誠実性・感情の安定"),
        img("だから、うまくいっていないことを", 5, "group_g", "【決め文の保持】人が集まって声を合わせる絵に替え、伝わる場所まで行かないといけないという決め文と間2.5秒を持たせる（映像レビュー④: 決め文を夜のスマホで受けない）"),
        img("僕、プロフィールを書き直すのは", 6, "group_g", "【方針の転換】同じ絵のまま、書き直すのをやめると言うところまで尺を分ける"),
        img("書き直すより、同じ人と何回か会える場所", 7, "group_f", "【象徴的な最後の一枚】何人かで同じ作業をしている場面で終え、アウトロへつなぐ"),
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
