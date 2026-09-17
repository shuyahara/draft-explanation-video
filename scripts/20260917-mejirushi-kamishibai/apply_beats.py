"""めたん×ずんだもん版「めじるしアクセサリーはなぜ流行ったのか」（Issue #40・8シーン）: ビート
（貼り写真 / 章カード / 黒板文字 / チョーク図解）と readings・pause_after を YAML に貼り直す。

  .venv\\Scripts\\python.exe scripts/20260917-mejirushi-kamishibai/apply_beats.py

冒頭で台本 md から YAML（narration 部）を **毎回生成し直す**（台本は推敲で動くため、
手で生成コマンドを打つのを忘れて古い narration にビートを貼る事故を防ぐ）。生成は

  python tools/kamishibai_md_to_yaml.py <台本md> --v5-yaml <同フォルダの empty-v5-stub.yaml>
      --out <同名yaml> --bgm ../bgm/aozora-ni-kuchibue.mp3
      --bgm-credit "BGM:「青空に口笛」のる（DOVA-SYNDROME）" --puppet-sink 0.12 --tempo 1.1

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（比較版・淫夢版などと同じ方式）。

貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-mejirushi/scene_NN_beat{slot}.*`
（配置は stage_assets.py）。

---------------------------------------------------------------------------
設計メモ（2026-09-17。台本 v3 に対応。オーケストレーターへの報告と同じ内容）
---------------------------------------------------------------------------
■ S2「黒板文字」と「貼り写真」の競合（2026-09-17 preflight で1回設計変更）
  台本の画面欄は、黒板（6年間の年表・4行累積）と貼り写真（傘チャーム→フリマアプリ→白紙掲示→
  電車）の両方を、重なる区間のアンカーで指定している（紙芝居モードは板と写真を同時に出せない
  ため、両方を文字どおり実装すると矛盾する）。最初は板を早期（cue1）から出して段階的に書き足す
  設計にしたが、板の1区間が34秒に達し「板だけの区間は10秒以内」（dialogue-guide.md §6）に
  抵触した。板の内容（日付の年表）は narration の進行と厳密に同期させる必然性が薄いため、
  **板は最後にまとめて1回だけ出す**方式に変更した:
    image(傘チャーム。冒頭〜静かな時期) → image(同写真+telopでコラボ拡大) →
    image(フリマアプリ。転売の実写) → image(同写真+telopでトレンド1位) →
    image(白紙掲示。販売中止の実写) → board(4行を1回で完成形として出す。9.5秒) →
    image(電車。決め文まで保持)
  出典クレジットは板に持たせられない（board に credit フィールドが無い）ため、フリマアプリ写真に
  LASISA、白紙掲示写真に J-CAST、電車写真にバンダイ公式・ガシャポン公式の残り出典をまとめて
  割り当てた。章カードの背景は「傘の持ち手のチャーム」の指定どおり、シーン最初の image ビート
  （umbrella 再利用）が自動で使われる。

■ S3 の板と写真（コーディネーター指示 2026-09-17 で確定）
  「それから、『めじるしおばさん』」で板に4行目を書き足した直後、「そういう人たちを」のキューで
  駅ナカ写真（s03_station_gen）に戻す。「Xで」の説明中に板を保持する旧方針は取り消し済み（板の
  終端はそのまま「それから、『めじるしおばさん』」〜「そういう人たちを」の手前まで＝実質Xでの
  説明中も保持されるが、これは"板を維持する意図"ではなく単に次の写真ビートの開始点がそこだから）。
  「僕も朝から並んだのだ」で S1 の行列写真に戻すのは変更なし。

■ S3 の板の行数（4行制限との整合）
  台本は「①Z世代の女子中高生 ②30〜40代の大人 ③親子・推し活 ④『めじるしおばさん』」の
  見出し込み5行を指定しているが、board は見出し込み最大4行（schema.md）。②と③（どちらも
  「大人の収集者」という近い理由）を1行に圧縮し、見出し+3項目の4行に収めた
  （dialogue-guide.md §6 の板の書き方規則⑥「要点に圧縮」に従う）。

■ 図解4か所（台本どおりの型: S4 sketch／S5 narrative row + chart／S6 sketch／S7 sketch）
  sketch を3シーンで使う点は diagram-guide.md の「同一型は2回まで」目安を超えるが、台本
  「トーン設計」欄が最初から図解4か所（うち sketch 3）を明示しているため、上位ドキュメントの
  目安より台本自身の指定を優先した（3枚とも構成が異なる: S4=2列2段、S6=2列+下段収束、
  S7=2列のみ）。chart は S5 の1箇所のみ（動画1本につき1箇所の上限を厳守）。

■ 素材の割り当て（候補は 素材メモ.md・2026-09-17）
  生成11枚は台本の割り当てどおりそのまま使用（キャラ無しの無地チャームのみ）。ストックは
  各アンカー3候補から1枚を選定: S2 フリマアプリ=s02_flea_app_2_pexels（画面がはっきり写る）、
  S4 ヘッドホン=s04_headphones_2_pexels（通勤中に聴く場面で「音楽を聴く人」の情景に合う）、
  S5 行列=s05_queue_3_pexels（後ろ姿の行列そのもの）、S6 傘立て=s06_umbrellas_1_pexels
  （傘立てのラック。台本の「傘立てに並ぶ」に最も忠実）、S7 名前を考える手元=s07_notebook_2_pexels
  （汎用のノート書き込み。「両親」が写る超音波写真候補は「名前を書く」動作ではないため不採用。
  オーケストレーターの再判断歓迎）。s02_flea_app の残り2候補・s04/s05/s06/s07 の残り候補は不使用。
"""
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
REPO = HERE.parents[1]
YAML_PATH = HERE / "20260917-mejirushi-kamishibai.yaml"
MD_PATH = HERE / "20260917-mejirushi-kamishibai.md"

# 出典表記（貼り写真の下＝字幕帯の右下）。素材メモ.md の候補一覧から転記。
CREDIT = {
    "bag5": "Image: AI generated",
    "line": "Image: AI generated",
    "umbrella": "Image: AI generated",
    "notice": "Image: AI generated",
    "train": "Image: AI generated",
    "station": "Image: AI generated",
    "site": "Image: AI generated",
    "lines": "Image: AI generated",
    "three_bags": "Image: AI generated",
    "wristband": "Image: AI generated",
    "bag1": "Image: AI generated",
    "market": "Image: AI generated",
    "headphones": "Photo: Burst / Pexels",
    "queue": "Photo: Pixabay",
    "umbrellas": "Photo: Iban Lopez Luna / Pexels",
    "names": "Image: AI generated",
}

# 採用元ファイル（candidates-mejirushi/{gen,stock}/{ファイル名}）→ render-assets へ配置するときの対応。
SOURCE_FILE = {
    "bag5": "gen/s01_bag5_gen.jpg",
    "line": "gen/s01_line_gen.jpg",
    "umbrella": "gen/s01_umbrella_gen.jpg",
    "notice": "gen/s02_notice_gen.jpg",
    "train": "gen/s02_train_gen.jpg",
    "station": "gen/s03_station_gen.jpg",
    "site": "gen/s04_site_gen.jpg",
    "lines": "gen/s05_lines_gen.jpg",
    "three_bags": "gen/s06_three_bags_gen.jpg",
    "wristband": "gen/s06_wristband_gen.jpg",
    "bag1": "gen/s08_bag1_gen.jpg",
    "market": "gen/s02_market_gen.jpg",
    "headphones": "stock/s04_headphones_2_pexels.jpg",
    "queue": "stock/s05_queue_1_pixabay.jpg",
    "umbrellas": "stock/s06_umbrellas_2_pexels.jpg",
    "names": "gen/s07_names_gen.jpg",
}

# 台本「発音・ポーズメモ」の読み。誤読の疑いがある語だけ登録する（正しく読む語を登録すると
# 複合語の読みが壊れるため）。preflight（VOICEVOX audio_query の読み突合）で確認する。
GLOBAL_READINGS: list[tuple[str, str]] = [
    ("お文具といっしょ", "オブングトイッショ"),
    ("Z世代", "ゼットセダイ"),
    ("X", "エックス"),
    ("推し活", "オシカツ"),
    ("48曲", "ヨンジュウハッキョク"),
    ("UCLA", "ユーシーエルエー"),
    ("99.9%", "キュウジュウキュウテンキュウパーセント"),
    ("ル・マンス", "ルマンス"),
]
EXTRA_READINGS: dict[int, list[tuple[str, str]]] = {}

# 台本「発音・ポーズメモ」のうち（間 N）で明示済みでないもの（生成側の既定値＝話者交代0.45・
# 文境界0.35・章末1.2 から動かす箇所だけ）。tempo=1.1 プリセット。
PAUSE_OVERRIDES: dict[int, list[tuple[str, float]]] = {
    1: [
        ("知ってる？", 0.8),
        ("形は今と同じよ", 1.0),
        ("並んだ理由の方にあるわ", 1.6),  # 間レビュー: 導入部最大の反転、直後が章カード
    ],
    2: [
        ("静かなものだったの", 0.6),
        ("販売をやめた店も出たわ", 0.6),
        ("混雑をやわらげるため", 0.8),
        ("街で見かける数よ", 1.6),  # 間レビュー: 決め文だが直後にずんだもんの反論
        ("どんな人が買ってるのだ", 0.8),  # 間レビュー: 章カードなしで回答が続く
    ],
    3: [
        ("悪口なのだ", 0.6),
        ("僕も朝から並んだのだ", 0.8),
        ("うまくいかないのよ", 1.2),  # 間レビュー: 直後が問い返し
    ],
    4: [
        ("別々に積み上がるの", 0.6),
        ("曲は同じなのに", 0.6),
        ("先に押した人で決まっていたのよ", 1.8),  # 間レビュー: 直後が即時の発見
    ],
    5: [
        ("考えてみて", 0.6),
        ("もう決まるのだ", 0.6),
        ("見えてる答えなのに", 0.6),
        ("人の標準装備よ", 1.8),  # 間レビュー: 直後に自分事の反応
    ],
    6: [
        ("おかしいと思わない", 0.8),
        ("私が考えたことだけどね", 0.6),
        ("めじるしおばさん」って言葉も", 0.6),
        ("折り返しが近いのかもしれない", 1.5),  # 間レビュー
    ],
    7: [
        ("早く消えるのだ", 0.6),
        ("僕のは、どっちなのだ", 0.8),
        ("そのまま残るわ", 2.0),  # 間レビュー: 直後が内省
    ],
    8: [
        ("見直してみるのだ", 0.6),
        ("これだけ残すのだ", 0.8),
        ("頑張って、ずんだもん", 0.8),
        ("これだけ残すのだ", 1.2),  # 間レビュー: 選択が確定する決め文
        ("頑張って、ずんだもん", 0.6),  # 間レビュー: 最後のオチへの振り
        ("傘の目印にもなるのだ", 2.0),  # 間レビュー: 終幕の保持
    ],
}


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
    # ---------------- S1 フック（じゃら付けのずんだもん） ----------------
    1: [
        img(None, 1, "bag5", "【冒頭】バッグに5個ぶら下がったチャームの手元で開く"),
        img("開店前から並んだのだ", 2, "line", "【行列の実写】ガシャポン店前の行列に替え、朝から並んだ様子を示す"),
        img("6年前？", 3, "line", "【保持の分割】同じ行列写真を保持したまま20秒超を避けるための継続カット"),
        img("2020年の6月よ", 4, "umbrella", "【発売当時】傘の持ち手のチャームに替え、6年前の発売時点を示す",
            telop="2020年6月発売・200円",
            source="バンダイ公式商品ページ"),
        img("同じものなのに", 5, "umbrella", "【保持の分割】同じ傘チャーム写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S2 6年間に何があったのか ----------------
    2: [
        chapter(),
        img(None, 1, "umbrella", "【冒頭】傘の持ち手のチャーム（S1と同じ）を背景に、静かだった発売当時から始める"),
        img("同じ年の10月に第2弾", 2, "umbrella", "【保持の分割】同じ傘チャーム写真を保持したまま20秒超を避けるための継続カット"),
        img("2024年に入ると", 3, "umbrella", "【保持の分割】同じ傘チャーム写真を保持したまま、コラボ拡大の事実をテロップで出す",
            telop="2024年 コラボ拡大・300円に"),
        img("メルカリで高値で転売されたの", 3, "market", "【転売の実写】汎用フリマアプリの画面を見る手元（生成）に替え、転売の事実を実写で見せる"
            "（2026-09-17: ストック候補にTEMUの実在ロゴが写り込むため生成画像へ差し替え）",
            source="LASISA（2026-05-22）"),
        img("6月、10代20代の女性に聞いた", 4, "market", "【保持の分割】同じフリマアプリ写真を保持したまま、トレンド調査の出典をテロップで出す",
            telop="モノ部門1位・売り切れ続出（2026年6月）",
            source="マイナビTrepo（2026-06-01）／日本経済新聞（2026-06）"),
        img("販売をやめたの", 5, "notice", "【販売中止の実写】ガシャポン機に貼られた白紙の掲示に替え、混雑緩和での販売中止を示す",
            source="J-CAST（2026-09-15）"),
        board("混雑をやわらげるため", "【年表まとめ】板を出し、6年間の年表を4行いっぺんに示す（板だけの区間を10秒以内に収めるため、"
              "個別の書き足しではなく完成形を1回で見せる設計に変更。2026-09-17）",
              telop="めじるしアクセサリーの6年\n2020年 発売 → 2024年 拡大\n2026年5-6月 転売・売り切れ\n2026年9月 販売中止"),
        img("商品はほとんど変わっていない", 6, "train", "【今の街へ】電車内でチャームを付けた乗客の写真に替え、決め文『いちばん変わったのは、街で見かける数よ』を保持したまま間を聞かせる",
            source="バンダイ公式商品ページ／ガシャポン公式"),
    ],
    # ---------------- S3 誰が付けているのか（章カードなし・S2の問いの続き） ----------------
    3: [
        img(None, 1, "station", "【冒頭】駅ナカのガチャコーナーに並ぶ大人たちで開く"),
        img("最初から若い女性にしか聞いていない", 2, "station", "【保持の分割】同じ駅ナカ写真を保持したまま、調査の出典をテロップで出す（20秒超も回避）",
            telop="10〜20代女性1,000人の調査（2026年6月）"),
        board("報道でいちばん多いのは", "【噂1/3】見出し＋①Z世代の女子中高生を出す",
              telop="噂される購入層\n①Z世代の女子中高生"),
        board("次に多いのが", "【噂2/3】②30〜40代・推し活層を書き足す（台本の②③を1行に圧縮。board最大4行のため。板だけの区間が10秒超になるのを避けるため①より早く出す）",
              telop="噂される購入層\n①Z世代の女子中高生\n②30〜40代・推し活層"),
        board("それから、「めじるしおばさん」", "【噂3/3】③『めじるしおばさん』を書き足して4行そろえる",
              telop="噂される購入層\n①Z世代の女子中高生\n②30〜40代・推し活層\n③『めじるしおばさん』"),
        img("そういう人たちを", 2, "station", "【板を外す】板を終え、駅ナカ写真に戻す（刺激的な語を長く見せない。2026-09-17コーディネーター指示）"),
        img("僕も朝から並んだのだ", 4, "line", "【S1へ戻す】行列写真（S1と同じ）に戻し、決め文『うまくいかないのよ』まで保持"),
        img("同時に言われている", 5, "line", "【保持の分割】同じ行列写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S4 人気は何で決まるのか ----------------
    4: [
        chapter(),
        img(None, 1, "headphones", "【冒頭】ヘッドホンで音楽を聴く人（ストック）で開く"),
        img("1万4千人を集めて", 2, "site", "【実験の場面】パソコン画面に曲リストが並ぶ生成画像に替え、実験用サイトを示す",
            telop="コロンビア大学 14,341人・48曲（2006）",
            source="Salganik, Dodds & Watts (2006). Science, 311(5762), 854-856."),
        img("互いに交わらない8つの", 3, "site", "【保持の分割】同じパソコン画面の写真を保持したまま20秒超を避けるための継続カット"),
        diagram(
            "数字を見せた世界では",
            "【逆転の構造】数字を見せない世界（なだらか）と見せる8世界（順位バラバラ）を2列で対比し、"
            "決め文『先に押した人で決まっていたのよ』（間2.5）まで保持する",
            sketch(
                [
                    [
                        cell("hide", icon="visibility_off", text="見せない世界", at="数字を見せた世界では", after="数字を見せた世界では"),
                        cell("show", icon="visibility", text="見せる8世界", at="バラバラだったの", after="バラバラだったの"),
                    ],
                    [
                        cell("hide_res", icon="trending_flat", text="人気は均等", at="数字を見せた世界では", after="数字を見せた世界では"),
                        cell("show_res", icon="shuffle", text="順位はバラバラ", at="バラバラだったの", after="バラバラだったの"),
                    ],
                ],
                highlight={"ids": ["show", "show_res"], "at": "先に押した人で", "after": "先に押した人で"},
                caption={"text": "同じ曲でも世界で順位が違う", "at": "先に押した人で", "after": "先に押した人で"},
            ),
        ),
        img("街でぶら下がってる数が", 3, "train", "【S2へ戻す】電車の写真（S2と同じ）に戻し、めじるしへの当てはめへつなぐ"),
        img("6年前は街で見かけなかった", 4, "train", "【保持の分割】同じ電車写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S5 なぜ他人に合わせるのか ----------------
    5: [
        chapter(),
        img(None, 1, "queue", "【冒頭】行列の後ろ姿（ストック）で開く"),
        img("1992年", 2, "queue", "【保持の分割】同じ行列写真を保持したまま、情報カスケードの出典をテロップで出す",
            telop="UCLA 3人の経済学者（1992）",
            source="Bikhchandani, Hirshleifer & Welch (1992). J. Political Economy, 100(5)."),
        diagram(
            "10人並べば",
            "【カスケードの可視化】先頭から人が同じ選択に点灯していく様を横一列で見せる。"
            "行列ができる確率が99.9%を超える点をキャプションで示す",
            {
                "type": "narrative",
                "layout": "row",
                "count": 10,
                "icon": "person",
                "select": {"at": "10人並べば", "after": "10人並べば", "lit": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
                "caption": {"text": "10人並べば99.9%超", "at": "10人並べば", "after": "10人並べば"},
            },
        ),
        img("線の長さを答えるだけの実験", 3, "lines", "【アッシュ実験の場面】机上のカードに縦線が並ぶ実験室の生成画像に替え、線の長さ課題を示す"),
        img("1955年", 4, "lines", "【保持の分割】同じ実験室写真を保持したまま、アッシュ実験の出典をテロップで出す",
            telop="スワースモア大学 123人（1955）",
            source="Asch (1955). Scientific American, 193(5), 31-35."),
        img("本当の参加者は", 5, "lines", "【保持の分割】同じ実験室写真を保持したまま20秒超を避けるための継続カット"),
        diagram(
            "面白いのは人数よ",
            "【誤答率の逆転】相手の人数1〜4人と、引きずられた答えの割合（3.6%/13.6%/31.8%/35.1%）を棒で見せる。"
            "3人以降が頭打ちになる点が見どころ（動画で唯一のchart）",
            {
                "type": "chart",
                "chart": "bar",
                "title": "同調した割合",
                "unit": "%",
                "source": "Asch (1955). Scientific American, 193(5), 31-35.",
                "series": [
                    {
                        "color": "accent",
                        "at": "面白いのは人数よ",
                        "after": "面白いのは人数よ",
                        "points": [
                            {"label": "1人", "value": 3.6},
                            {"label": "2人", "value": 13.6},
                            {"label": "3人", "value": 31.8},
                            {"label": "4人", "value": 35.1},
                        ],
                    }
                ],
            },
        ),
        img("電車で3人が付けてたら", 4, "train", "【S2へ戻す】電車の写真（S2と同じ）に戻し、決め文『人の標準装備よ』（間2.5）まで保持"),
    ],
    # ---------------- S6 なぜ「目印」だったのか ----------------
    6: [
        chapter(),
        img(None, 1, "umbrellas", "【冒頭】たたまれた傘が積み重なる情景（ストック）で開く"
            "（2026-09-17: 旧候補は傘2本のみでほぼ空だったため、傘が並ぶ候補に差し替え）"),
        img("全員が同じものを付けている", 2, "three_bags", "【矛盾の提示】同じバッグに違う色のチャームが付いた3人の手元の生成画像に替える"),
        img("欲しくなる理由には", 3, "three_bags", "【保持の分割】同じ写真を保持したまま20秒超を避けるための継続カット"),
        img("後ろがスノッブ効果", 4, "three_bags", "【保持の分割】同じ写真を保持したまま、命名の出典をテロップで出す",
            telop="バンドワゴン効果／スノッブ効果（1950）",
            source="Leibenstein (1950). Quarterly Journal of Economics, 64(2), 183-207."),
        diagram(
            "同じブランドの同じ枠の中で",
            "【両立の構造】左『みんなと同じ』右『私だけ違う』の2列から、下段『両方満たす』へ収束させる。"
            "『商品を見て私が考えたことだけどね』（推論の限定）まで保持する",
            sketch(
                [
                    [
                        cell("same", icon="group", text="みんなと同じ", at="同じブランドの同じ枠の中で", after="同じブランドの同じ枠の中で"),
                        cell("diff", icon="face", text="私だけ違う", at="キャラだけが違うの", after="キャラだけが違うの"),
                    ],
                    [
                        cell("both", icon="join_inner", value="300円", text="両方満たす", at="一つで両方満たせるのよ", after="一つで両方満たせるのよ"),
                        None,
                    ],
                ],
                arrows=[("same", "both"), ("diff", "both")],
                highlight={"ids": ["both"], "at": "一つで両方満たせるのよ", "after": "一つで両方満たせるのよ"},
            ),
        ),
        img("あるリストバンドを着けていた大学生たち", 5, "wristband", "【逆向きの研究】手首にリストバンドを着けた学生たちの生成画像に替える",
            source="Berger & Heath (2008). JPSP, 95(3), 593-607."),
        diagram(
            "隣の寮の学生が同じものを着け始めた途端",
            "【研究の結果を可視化】着用→隣の寮も着用→みんな外す、の一本鎖で離脱の結果を見せる"
            "（2026-09-17: 画像突合レポートでBerger&Heathの結果が視覚化されていないと指摘されたため追加）。"
            "『ペンシルベニア大学のジョナ・バーガーたちが』まで保持する",
            {
                "type": "narrative",
                "layout": "chain",
                "items": [
                    {"id": "wear", "text": "同じリストバンドを着ける", "icon": "watch",
                     "at": "隣の寮の学生が同じものを着け始めた途端", "after": "隣の寮の"},
                    {"id": "copy", "text": "隣の寮も着け始める", "icon": "group",
                     "at": "隣の寮の学生が同じものを着け始めた途端", "after": "着け始めた途端"},
                    {"id": "remove", "text": "みんな外す", "icon": "remove",
                     "at": "隣の寮の学生が同じものを着け始めた途端", "after": "みんな外したの"},
                ],
            },
        ),
        img("「めじるしおばさん」って言葉も", 7, "station", "【S3へ戻す】駅ナカ写真（S3と同じ）に戻し、決め文『折り返しが近いのかもしれない』（間2.0）まで保持"),
        img("ブーム、早く終わってほしい", 8, "station", "【保持の分割】同じ駅ナカ写真を保持したまま20秒超を避けるための継続カット"),
    ],
    # ---------------- S7 このブームはどうなるのか ----------------
    7: [
        chapter(),
        img(None, 1, "names", "【冒頭】両親の手元がノートに赤ちゃんの名前候補を書く情景（生成）で開く"
            "（2026-09-17: ストックの汎用ノート書き込み写真は『名前を考える』感が弱いため生成画像へ差し替え）",
            source="Berger & Le Mens (2009). PNAS, 106(20), 8146-8150."),
        diagram(
            "急に人気が上がった名前ほど",
            "【山の形の対比】左『急に上がって急に落ちる』（高く細い山）、右『ゆっくり上下』（低く広い山）を2列で見せる",
            sketch(
                [
                    [
                        cell("fast", icon="trending_up", text="急に上がり急落", at="急に人気が上がった名前ほど", after="急に人気が上がった名前ほど"),
                        cell("slow", icon="trending_flat", text="ゆっくり上下", at="避けていたの", after="避けていたの"),
                    ],
                ],
                caption={"text": "山が高いほど早く沈む", "at": "避けていたの", "after": "避けていたの"},
            ),
        ),
        img("転売、買い占め、販売中止は", 2, "notice", "【S2へ戻す】白紙掲示の写真（S2と同じ）に戻し、めじるしの現状を重ねる"),
        img("自分の推しだから持っているものは", 3, "bag5", "【S1へ戻す】5個のバッグの手元（S1と同じ）に戻し、決め文『そのまま残るわ』（間2.5）まで保持"),
    ],
    # ---------------- S8 結び（商品は同じ、変わったのは周り） ----------------
    8: [
        board("それで、6年前と今で", "【結び1/3】見出しのみを出す",
              telop="なぜ流行ったのか"),
        board("商品はほとんど同じで", "【結び2/3】①②を書き足す（1文に両方の事実が含まれるため同時に出す）",
              telop="なぜ流行ったのか\n① 商品は6年間ほぼ同じ\n② 変わったのは、周りが持っているか"),
        board("人は品質より、他人の選択を見て買う", "【結び3/3】③を書き足して4行そろえる",
              telop="なぜ流行ったのか\n① 商品は6年間ほぼ同じ\n② 変わったのは、周りが持っているか\n③ 品質より、他人の選択を見る"),
        img("僕のバッグの5個", 1, "bag5", "【板を外す】5個のバッグの手元（S1と同じ）に戻し、見直しの場面へ"),
        img("これだけ残すのだ", 2, "bag1", "【1個だけに】チャーム1個だけのバッグの生成画像に替え、本当に好きな1個だけが残る様子を示す"),
        img("傘の目印にもなるのだ", 3, "umbrella", "【象徴的な最後の一枚】傘の持ち手のチャーム（S1と同じ）で終え、アウトロへつなぐ"),
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
