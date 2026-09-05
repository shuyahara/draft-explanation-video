"""ずんだもん版・冷笑: ビート（貼り写真 / 黒板のみ / 章カード / チョーク図解）と追加 readings を
YAML に貼り直す。

セリフを推敲すると字幕キュー番号がずれるので、ビートの開始位置は「そのキュー本文に含まれる
アンカー文字列」で指定し、実行時にキュー番号へ解決する（ドパガキ版 apply_beats.py と同じ方式）。

  .venv\\Scripts\\python.exe scripts/20260905-cynicism-kamishibai/apply_beats.py

前提: tools/kamishibai_md_to_yaml.py で YAML（narration 部）を生成済み。
貼り写真は `C:/Users/shuya/Projects/assets-kamishibai/render-assets-cynicism/scene_NN_beat{slot}.*`。
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

YAML_PATH = Path(__file__).with_name("20260905-cynicism-kamishibai.yaml")

# 出典表記（字幕帯右下）。キー = 写真の種類。実ファイルの作者名は manifest から転記する。
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

# 元 YAML（ナレーション版）から転記されない読み。(surface, reading) をシーンに追加する。
EXTRA_READINGS = {
    1: [("口の端", "クチノハ")],
    4: [("甕", "カメ")],
    7: [("無力感", "ムリョクカン")],   # VOICEVOX が「ムリキカン」と読む（v2 ASR チェックで発見）
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


BEATS = {
    1: [
        img(None, 1, "train", "【昼の電車】肩越しに見るスマホの画面。冒頭の場面をそのまま"),
        img("返信も見て", 2, "reply", "【返信欄】返信の並ぶ画面を見る手元（別カット）"),
        board("そういう笑いのことを、冷笑って呼ぶのよ", "【定義】写真をはずし、黒板に冷笑の定義を書く",
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
        img("人々は彼を、「犬」と呼んだの", 5, "dog", "【犬】遺跡にいる犬"),
        img("もうひとつ、神託の話があるわ", 6, "delphi", "【神託】デルフォイの遺跡"),
        board("という呼び名がシニシズムの語源", "【決め文】写真をはずし、語源を黒板に",
              telop="犬（キュオーン）→ シニシズム"),
    ],
    4: [
        img(None, 1, "waterhouse", "【犬のような者たち】ウォーターハウス「ディオゲネス」", telop="キュオーン（犬）→ キュニコス（犬のような者たち）→ Cynic"),
        board("フランスの哲学者ミシェル・フーコー", "【真理の勇気】写真をはずし、出典を黒板に", telop="Foucault『真理の勇気』（1983-84 講義）／ Mazella (2007)"),
        img("英語のシニックが", 2, "dictionary", "【19世紀の語義】古い辞書のページ（文字は読めない）"),
        diagram("文学研究者のデイヴィッド・マゼラ", "【図解: 反転の三証言】近代の冷笑を中心に、マゼラ・スローターダイク・ジジェクの言い換えが放射し、決め文で色が転じる（状態変化が主張）",
                {"type": "narrative", "layout": "radiate",
                 "center": {"icon": "psychology", "text": "近代の冷笑", "at": "文学研究者のデイヴィッド・マゼラ"},
                 "items": [
                     {"id": "mazella", "text": "鍛錬から無関心へ", "at": "昔は欲望を抑える鍛錬だったものが"},
                     {"id": "sloterdijk", "text": "知っていて動かない", "at": "近代の、知っていながら動かない態度が"},
                     {"id": "zizek", "text": "欺瞞と知って続ける", "at": "「それが欺瞞だと知っている"},
                 ],
                 "turn": {"at": "今の冷笑は、本気に吠えている"}}),
    ],
    5: [
        chapter(),
        img(None, 1, "fundraiser", "【募金の横を通り過ぎる】街頭の呼びかけを見ずに通る人々",
            telop="津田正太郎（慶應義塾大学）現代ビジネス"),
        board("「あの人はカネのためにやっている」", "【動機を疑う】写真をはずし、三つの決めつけを黒板に", telop="「カネのため」「売名だ」「ポーズだ」→ 中身を考えなくて済む"),
        board("批判する側も、擁護する側も", "【決めつけ合い】ポスターは描かず、二人だけで"),
        board("冷笑の第一の安さは", "【決め文】黒板に第一の安さ", telop="第一の安さ：考えなくて済む"),
    ],
    6: [
        img(None, 1, "meeting", "【腕を組んで見ている人】会議室で椅子にもたれる後ろ姿",
            telop="Stavrova & Ehlebracht (2019) PSPB"),
        board("ずんだもんと同じ答えの人", "【数字】写真をはずし、割合を黒板に",
              telop="「皮肉屋の方が賢い」と答えた人 56〜70%（米・独・英）"),
        board("しかも、その「賢そう」という印象は", "【決め文】第二の安さ", telop="第二の安さ：何もしなくても賢い側に立てる"),
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
        img("日本財団が2019年に行った", 1, "election", "【日本の若者】選挙ポスター掲示板の前を通る人々",
            telop="「自分で国や社会を変えられる」日本 18.3%（9カ国中最下位）"),
        board("と思っていると、変えようとする人まで", "【前提】写真をはずし、前提を黒板に", telop="「どうせ変わらない」→ 変えようとする人が愚か者に見える"),
        img("哲学者のヤン・エルスターは", 2, "aesop", "【酸っぱい葡萄】ナレーション自身の比喩を PD 挿絵で"),
        board("社会なんて変えられないと思うと", "【決め文】写真をはずし、狐と冷笑を重ねる"),
    ],
    8: [
        img(None, 1, "veg", "【ベジタリアン】野菜の食卓", telop="Minson & Monin (2012) SPPS"),
        diagram("47パーセントの人が", "【図解: 善行者への貶め】道徳的な相手→責められる予期→貶める、の一本鎖",
                {"type": "narrative", "layout": "chain",
                 "items": [
                     {"id": "moral", "text": "道徳的な相手", "icon": "volunteer_activism", "at": "47パーセントの人が"},
                     {"id": "expect", "text": "責められる予期", "icon": "psychology_alt", "at": "とくに否定的だった人ほど"},
                     {"id": "derog", "text": "相手を貶める", "icon": "thumb_down", "at": "「そう思われそう」と感じただけで", "after": "感じただけで"},
                 ],
                 "caption": {"at": "研究チームはこれを", "text": "善行者への貶め"}}),
        img("2008年の実験では、もっとはっきり", 2, "lab", "【2008年の実験】実験室で課題に向かう参加者の後ろ姿",
            telop="Monin, Sawyer & Marquez (2008) JPSP"),
        img("ここで、冒頭の画面に戻って", 3, "train", "【冒頭の再演】電車のスマホ画面を再掲"),
        board("この実験で嫌われたのは", "【決め文】写真をはずし、二人だけで"),
    ],
    9: [
        img(None, 1, "lab2", "【映像を見る参加者】モニターの前の後ろ姿", telop="Smith et al. (1996) PSPB"),
        img("オーストラリアのフリンダース大学", 2, "bulletin", "【高く昇った人】掲示板を見上げる学生たち",
            telop="Feather (1989)／Feather & Sherman (2002)"),
        img("オーストラリアには、「高く伸びた芥子", 3, "poppy", "【高く伸びた芥子】一本だけ高い花。ナレーション自身の比喩",
            telop="高く伸びた芥子は刈り取られる（Tall Poppy）"),
        board("自分と似た立場の誰かが", "【決め文】写真をはずし、棘の出どころを聞かせる"),
        board("少し違いがあるの", "【留保】予測したのは憤り", telop="転落を喜ぶ気持ちを予測したのは「不当だ」という憤り"),
    ],
    10: [
        board(None, "【二つの軸】写真なし。温かさ×有能さを言葉で", telop="Fiske, Cuddy, Glick & Xu (2002) JPSP"),
        img("本気で何かを変えようとする人は、まだ成果が", 1, "beach", "【ボランティア】海岸清掃の人々（遠景）。冒頭の投稿の中身"),
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
        img("同じチームがアメリカの全国調査", 2, "payslip", "【9年後の収入】給与明細を持つ手（文字は読めない）",
            telop="Stavrova & Ehlebracht (2016) JPSP"),
        img("2024年には、もっと切ない結果", 3, "chair", "【リーダーに選ばれない】会議机の端の席",
            telop="Stavrova, Ehlebracht & Ren (2024) British Journal of Psychology"),
        img("仲間はずれの実験もあるのよ", 4, "outside", "【つながり直せない】輪の外に立つ一人の後ろ姿",
            telop="Choy, Eom & Li (2021) Personality and Individual Differences"),
        diagram("傷つく前に切り捨てるから", "【図解: 請求書】四つの代価を一本鎖で積む。ここまで一枚ずつ見せた項目を一望にする",
                {"type": "narrative", "layout": "chain",
                 "items": [
                     {"id": "cog", "text": "認知能力が低い", "icon": "school", "at": "傷つく前に切り捨てるから"},
                     {"id": "income", "text": "9年後の収入が低い", "icon": "payments", "at": "傷つく前に切り捨てるから"},
                     {"id": "leader", "text": "リーダーに選ばれない", "icon": "groups", "at": "傷つく前に切り捨てるから"},
                     {"id": "reconnect", "text": "つながり直せない", "icon": "link_off", "at": "傷つく前に切り捨てるから"},
                 ],
                 "caption": {"at": "傷つく前に切り捨てるから", "text": "安い知性の請求書"}}),
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
        board("画面を開くたびに", "【環境の産物】写真をはずし、決め文へ", telop="冷笑は、個人の性格である前に環境の産物"),
        img("政府への信頼は", 3, "diet", "【政府への信頼】国会議事堂",
            telop="政府への信頼 24%（OECD 2021）／社会を変えられる 18.3%"),
        board("日本で目立つのは", "【決め文】写真をはずす", telop="日本は「不信の国」ではなく「無力感の国」"),
        board("似た無力感は、ずっと前から", "【三無主義】年表を黒板に",
              telop="1972 連合赤軍事件 → 1973 オイルショック → 三無主義"),
        board("社会学者の北田暁大さん", "【皮肉な共同体】書名を黒板に", telop="北田暁大『嗤う日本の「ナショナリズム」』2005"),
    ],
    13: [
        img(None, 1, "report", "【懐疑＝道具】資料を読み込み付箋を貼る手", telop="Citrin & Stoker (2018) Annual Review of Political Science"),
        board("疑いが、状況を見て使う道具ではなく", "【道具か癖か】黒板に対比", telop="懐疑（道具）／ 冷笑（癖）"),
        img("……癖だったのだ", 2, "laptop", "【癖】見出しだけ見てノートPCを閉じる手"),
        board("スタンフォード大学の心理学者、ジャミール・ザキ", "【希望を持った懐疑】写真をはずし、決め文まで保持",
              telop="希望を持った懐疑（Zaki, Hope for Cynics 2024）"),
    ],
    14: [
        img(None, 1, "gerome", "【回帰】ランプの男へ戻る"),
        board("安全な場所から、何も賭けずに", "【削られるもの】写真をはずし、二人だけで"),
        img("もう一度思い出してみて", 2, "train", "【冒頭へ回帰】電車のスマホ画面を再掲"),
        board("冷笑は安い", "【決め文】写真をはずし、四つの決め文を黒板で受ける", telop="冷笑は安い。だから、広がる"),
        img("僕の親指、今日は", 3, "thumb", "【最後の一枚】親指が止まったままのスマホ。アウトロで保持"),
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


def resolve(cues: list[str], anchor: str | None, scene_id: int) -> int:
    if anchor is None:
        return 1
    for i, c in enumerate(cues, 1):
        if anchor in c:
            return i
    raise SystemExit(f"scene {scene_id}: anchor not found: {anchor!r}")


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
            if frm <= last_from:
                raise SystemExit(f"scene {sid}: from must increase ({anchor!r} -> {frm} <= {last_from})")
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
        extra = [(s, r) for s, r in EXTRA_READINGS.get(sid, []) if s in text]
        if extra:
            rs = scene.get("readings") or []
            have = {r["surface"] for r in rs}
            rs.extend({"surface": s, "reading": r} for s, r in extra if s not in have)
            scene["readings"] = rs
        print(f"scene {sid:>2}: {len(cues):>2} cues, {len(beats)} beats  from={[b.get('from') for b in beats if 'from' in b]}")
    with YAML_PATH.open("w", encoding="utf-8", newline="\n") as f:
        yaml.dump(doc, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"beats written: {total}")


if __name__ == "__main__":
    main()
