"""紙芝居版ドパガキ: ビート（貼り写真 / 黒板のみ / 章カード）を YAML に貼り直す。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する。

  .venv\\Scripts\\python.exe scripts/20260904-dopagaki-kamishibai/apply_beats.py

前提: tools/kamishibai_md_to_yaml.py で YAML（narration 部）を生成済み。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

YAML_PATH = Path(__file__).with_name("20260904-dopagaki-kamishibai.yaml")

CREDIT = {
    "bed": "Photo: cottonbro studio / Pexels",
    "hand": "Photo: cottonbro studio / Pexels",
    "train": "Photo: Muhamad Guruh Budi Hartono / Pexels",
    "cover": "Book cover: Dopamine Nation, Anna Lembke (Dutton, 2021)",
    "stairs": "Photo: Eren Li / Pexels",
    "lab": "Photo: Rámon van Raaij / Pexels",
    "juice": "Photo: Pixabay / Pexels",
    "stopwatch": "Photo: William Warby / Pexels",
    "data": "Photo: Pixabay / Pexels",
    "rat": "Photo: Nikolett Emmert / Pexels",
    "office": "Photo: David Kwewum / Pexels",
    "movie": "Photo: Bence Szemerey / Pexels",
    "cafe": "Photo: Ayşenur / Pexels",
    "papyrus": "Wikimedia Commons, Public Domain（大英博物館蔵『パピルス・オブ・アニ』）",
    "fragonard": "Wikimedia Commons, Public Domain（Fragonard, The Reader, c.1770）",
    "books": "Photo: Pixabay",
    "comics": "Photo: Jonathan Cooper / Pexels",
    "paper": "Photo: RDNE Stock project / Pexels",
    "classroom": "Photo: Kari Alfonso / Pexels",
    "library": "Photo: Pixabay",
    "capitol": "Photo: Guohua Song / Pexels",
    "skinner": "Photo: Pixabay / Pexels",
    "slot": "Photo: Vanessa V. / Pexels",
    "thumb": "Photo: Lisa Fotios / Pexels",
    "notif": "Photo: cottonbro studio / Pexels",
    "facedown": "Photo: Valentin Ilas / Pexels",
    "morning": "Photo: Chris Alo / Pexels",
}
KEIFU = "不安の系譜: 文字 → 小説 → 漫画 → 学力 → ショート動画？"


# (type, anchor, slot, credit_key, cut_reason, telop)
# anchor: そのキュー本文に含まれる文字列（シーン内で最初に一致したキューを開始位置にする）。None は先頭。
def img(anchor, slot, credit_key, why, telop=None):
    return ("image", anchor, slot, credit_key, why, telop)


def board(anchor, why, telop=None):
    return ("board", anchor, None, None, why, telop)


def chapter():
    return ("chapter", None, None, None, "【章の入口】黒板に問いを書いて本題へ", None)


BEATS = {
    1: [
        img(None, 1, "bed", "【夜ふかしの自白】ベッドで横になりスマホを見る人。枕元の明かり。冒頭の場面をそのまま見せる"),
        img("この前「ドパガキ」という言葉", 2, "hand", "【ドパガキという言葉】スマホの画面を見る手元。命名の場面へ",
            telop="ドパガキ＝ドーパミン中毒のガキ（ネットスラング）"),
        board("じゃあ今日は", "【問いの提示】写真をはずし、黒板に問いだけ", telop="なぜ現代人は、ドパガキになってしまうのか"),
        board("先に言っておくわ", "【冒頭の約束】犯人＝画面の設計、を黒板に大きく", telop="犯人＝画面の設計"),
    ],
    2: [
        img(None, 1, "train", "【通説の筋書き】昼の電車でスマホを見る人々"),
        img("よく知ってるわね", 2, "cover", "【世界的な広がり】書影（実物）を貼る", telop="Anna Lembke『Dopamine Nation』2021"),
        img("だから「ドーパミンが出すぎて", 3, "stairs", "【デトックス】スマホを引き出しにしまう手"),
        board("ただ、この説明には", "【決め文】写真をはずして間。反転の一撃", telop="ドーパミン ≠ 快楽物質"),
    ],
    3: [
        chapter(),
        img(None, 1, "lab", "【1997年の実験】実験に使われる種のサル（マカク）。v7 で脳波写真から差し替え", telop="Schultz et al., Science (1997)"),
        img("サルにジュースをあげると", 2, "juice", "【ジュースで発火】ジュースのグラス。報酬そのものを見せる"),
        board("でもね", "【奇妙なこと】写真をはずし、実験の核心（合図→ジュース、発火の移動）をチョークで示す",
              telop="合図 → ジュース ／ 発火は「合図」の瞬間へ移る"),
        board("そのとおり", "【報酬予測誤差】黒板に用語を書く", telop="報酬予測誤差 ＝ 予想と現実のズレ"),
    ],
    4: [
        img(None, 1, "rat", "【ラットの実験】実験動物の写真", telop="Berridge & Robinson (2016)"),
        board("ベリッジは、この二つを", "【二つの言葉】黒板に wanting / liking", telop="wanting（欲しい）／ liking（好き）"),
        img("それ、そのまんま", 2, "bed", "【冒頭の再演】昨夜のずんだもん＝冒頭の写真を再掲"),
        board("半分は当たっている", "【筋書きの差し替え】写真をはずし、二人だけで「溺れている→空回り」の言い換えを聞かせる。章末の問いまで保持",
              telop="「溺れている」のではなく「空回りしている」"),
    ],
    5: [
        img(None, 1, "office", "【47秒】ノート・スマホ・PC を同時に扱う手元（注意の分散）", telop="Gloria Mark（UC Irvine）"),
        img("マーク自身の振り返り", 4, "stopwatch", "【数字】ストップウォッチ＝画面を切り替えるまでの時間の計測。v7 で板だけから写真付きに", telop="2004年: 約2分半 → 近年: 平均47秒（中央値 40秒）"),
        img("好きな映画なら", 2, "movie", "【映画は2時間見られる】映画館"),
        img("面白い本なら", 3, "cafe", "【本は1時間読める】読書の場面"),
        board("少なくともこの数字だけでは", "【誤読の修正】写真をはずし、出典を残す", telop="Gloria Mark『Attention Span』(2023)"),
    ],
    6: [
        chapter(),
        img(None, 1, "papyrus", "【パイドロス】パピルスの実物", telop="プラトン『パイドロス』274-275"),
        board("新しいメディアが", "【系譜の始まり】黒板に系譜の一本線を書き始める", telop="不安の系譜: 文字 →"),
        img("時代は下って", 2, "fragonard", "【読書熱】18世紀の読書する女性（絵画）", telop="Lesewut（読書熱）18世紀末ドイツ"),
        img("1795年には", 3, "books", "【疫病だと断じる本】古書の山"),
        board("あれ。", "【同じ筋書き】写真をはずし、系譜を伸ばす", telop="不安の系譜: 文字 → 小説 →"),
    ],
    7: [
        img(None, 1, "comics", "【1954年】積まれた漫画本"),
        img("この話には、後日談", 2, "paper", "【後日談】資料を精査する手元", telop="Tilley, Information & Culture (2012)"),
        board("子供の年齢は", "【捏造の中身】写真をはずして聞かせる"),
        img("日本にも、似た繰り返し", 3, "classroom", "【学力パニック】試験を受ける生徒たちの教室", telop="PISA 読解力（OECD）2003年: 8位 → 14位"),
        board("2012年には4位まで戻った", "【順位の上下】写真をはずし、黒板に順位の推移を一本で書く（犯人だけが入れ替わる型を見せる）",
              telop="PISA 読解力 2003: 14位 → 2012: 4位 → 2018: 15位 → 2022: 3位"),
        board("こういう繰り返しには", "【モラルパニック】用語を黒板に", telop="moral panic（Cohen, 1972）"),
        board("文字、小説、漫画", "【系譜が伸びる】文字→小説→漫画→学力", telop="不安の系譜: 文字 → 小説 → 漫画 → 学力 → ？"),
    ],
    8: [
        chapter(),
        board(None, "【系譜の終点】ショート動画？ を書き足す", telop=KEIFU),
        img("グリフィス大学", 1, "library", "【メタ分析】学術誌の書架", telop="Nguyen et al., Psychological Bulletin (2025)：71研究・約9.8万人"),
        board("結論はこう", "【判定ボード1行目】関連：ある", telop="関連：ある（中程度）"),
        img("運営企業の内側", 2, "capitol", "【内部告発の証言】議会の建物", telop="米上院 商務委員会 公聴会 (2021)"),
        board("ただし、ここが大事", "【ただし】因果の向きは決められない", telop="関連：ある（中程度）／ 因果：決められない"),
        img("もうひとつ、規模", 3, "data", "【規模の数字】データ解析の画面（35万人分）。v7 で板だけから写真付きに", telop="Orben & Przybylski (2019)：説明できた個人差は 0.4%"),
        board("ここで一度整理", "【整理】判定ボード3行そろう。決め文まで保持", telop="関連：ある（中程度）／ 因果：決められない ／ 規模：大きくない"),
    ],
    9: [
        chapter(),
        img(None, 1, "skinner", "【スキナーの実験】研究者の手のひらの実験用マウス（装置写真は判読しづらく差し替え）", telop="可変比率強化（Ferster & Skinner, 1957）"),
        img("スロットマシンが人を離さない", 2, "slot", "【スロットマシン】カジノ"),
        img("おすすめ動画が次々に並ぶフィード", 3, "thumb", "【あなたのスマホ】フィードを親指で払う手元"),
        board("誰にも分からない", "【設計】写真をはずし、出典を黒板に", telop="Clark & Zack, Addictive Behaviors (2023)"),
        img("しかもスマホの画面は", 4, "thumb", "【段差の除去】無限スクロールの手元（再掲）"),
        board("ずんだもんが見ていたショート動画", "【決め文】長い決め文をチョークで短く残す", telop="急所を、正確に突く装置"),
    ],
    10: [
        img(None, 1, "bed", "【冒頭に戻る】同じ寝室の写真"),
        board("脳が弱くなったんじゃない", "【最大の決め文】写真をはずして間だけ"),
        img("通知をひとつ切る", 2, "notif", "【対策】通知を切る手元"),
        img("寝室の外で充電", 3, "facedown", "【寝室の外で充電】置かれたスマホ"),
        board("そのときは、自分を責める", "【救済の一文】写真をはずし、二人だけ"),
        img("今夜は、スマホを居間で", 4, "morning", "【朝】窓の外が明るむ寝室。アウトロで保持"),
    ],
}


def cues_of(scene) -> list[str]:
    """字幕キューの本文列。分割規則は script-to-video の `text_cues.split_into_sentences` と
    必ず同じものを使う（括弧内の 。！？ では切らない。ここがずれるとビート位置が全部ずれる）。"""
    sys.path.insert(0, "C:/Users/shuya/Projects/script-to-video/src")
    from script_to_video.text_cues import split_into_sentences

    out = []
    for seg in scene["narration"]:
        out.extend(p for p in split_into_sentences(seg["text"]) if p.strip())
    return out


def resolve(cues: list[str], anchor: str | None, scene_id: int) -> int:
    if anchor is None:
        return 1
    for i, c in enumerate(cues, 1):
        if anchor in c:
            return i
    raise SystemExit(f"scene {scene_id}: anchor not found: {anchor!r}")


def main() -> None:
    doc = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    total = 0
    for scene in doc["scenes"]:
        cues = cues_of(scene)
        beats = []
        last_from = 0
        for kind, anchor, slot, ckey, why, telop in BEATS[scene["id"]]:
            if kind == "chapter":
                beats.append({"type": "chapter", "cut_reason": why})
                continue
            frm = resolve(cues, anchor, scene["id"])
            if frm <= last_from:
                raise SystemExit(f"scene {scene['id']}: from must increase ({anchor!r} -> {frm} <= {last_from})")
            last_from = frm
            b = {"type": kind, "cut_reason": why, "from": frm}
            if kind == "image":
                b["slot"] = slot
                b["credit"] = CREDIT[ckey]
            if telop:
                b["telop"] = telop
            beats.append(b)
        scene["beats"] = beats
        total += len(beats)
        print(f"scene {scene['id']:>2}: {len(cues):>2} cues, {len(beats)} beats  from={[b.get('from') for b in beats if 'from' in b]}")
    with YAML_PATH.open("w", encoding="utf-8", newline="\n") as f:
        yaml.dump(doc, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"beats written: {total}")


if __name__ == "__main__":
    main()
