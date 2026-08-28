# -*- coding: utf-8 -*-
"""2026-08-27 rev2: シーン1を三人称に、シーン2にシニシズムの説明を追加し問いを1つに、
シーン3のtelop削除、シーン8・14の回帰文を三人称に合わせる。使い捨て編集スクリプト。"""
import io, re, shutil
from pathlib import Path

p = Path(r"C:\Users\shuya\Projects\draft-explanation-video\scripts\20260827-cynicism\20260827-cynicism.yaml")
shutil.copy(p, p.with_suffix(".v1.yaml.bak"))
s = p.read_text(encoding="utf-8")


def scene_span(s, sid):
    m = re.search(rf"^  - id: {sid}\n", s, re.M)
    a = m.start()
    m2 = re.search(rf"^  # =+\n  # シーン{sid + 1}", s[a:], re.M)
    b = a + m2.start() if m2 else len(s)
    return a, b


def replace_from_narration(s, sid, new_tail):
    a, b = scene_span(s, sid)
    chunk = s[a:b]
    i = chunk.index("    narration:\n")
    return s[:a] + chunk[:i] + new_tail + s[b:]


SCENE1 = '''    narration:
      - text: "昼の電車。"
        pause_after: 0.3
      - text: "誰かのスマートフォンの画面に、ひとつの投稿が流れてくる。"
        pause_after: 0.3
      - text: "海岸の清掃に参加しませんか、という呼びかけだ。"
        pause_after: 0.4
      - text: "その下に、返信が並んでいる。"
        pause_after: 0.3
      - text: "意識高いね。"
        pause_after: 0.3
      - text: "どうせ売名でしょ。"
        pause_after: 0.3
      - text: "はいはい。"
        pause_after: 0.5
      - text: "呼びかけについた反応は、数えるほどしかない。"
        pause_after: 0.3
      - text: "それを嗤った返信のほうが、何倍も広がっている。"
        pause_after: 0.6
      - text: "画面の上の指は、何事もなかったように、次の投稿へ滑っていく。"
        pause_after: 0.6
      - text: "こういう反応を、冷笑と呼ぶ。"
        pause_after: 0.4
      - text: "本気で何かをしようとする人を、一段高いところから、鼻で笑って済ませる態度のことだ。"
        pause_after: 1.0
    readings:
      - surface: "嗤った"
        reading: "ワラッタ"
      - surface: "冷笑"
        reading: "レイショウ"
    beats:
      - type: image
        from: 1
        slot: 1
        visual_intent: "昼の電車。誰かのスマートフォンの画面に投稿が流れてくる（三人称。画面を眺める視点）"
        cut_reason: "【冒頭の場面・三人称】キュー1〜3『昼の電車』『誰かのスマートフォンの画面に投稿が流れてくる』『海岸の清掃に参加しませんか』。前作の一人称（自分の指）ではなく、他人の画面で起きている冷笑を眺める画で開く"
        gen_prompt: "over-the-shoulder view on a bright daytime commuter train of a stranger's hand holding a smartphone, the screen showing a social feed layout with one post at the top, all text blurred and unreadable, no faces, soft window light, documentary still, no lettering"

      - type: image
        from: 4
        slot: 2
        visual_intent: "投稿の下に並ぶ短い返信。文字は読めないが、短い一行が三つ並んでいることは分かる"
        cut_reason: "【並ぶ返信】キュー4〜7『その下に返信が並んでいる』『意識高いね』『どうせ売名でしょ』『はいはい』。返信欄に寄り、三つの短い返信が並ぶ画で嗤いの言葉を受ける"
        gen_prompt: "close-up of a smartphone screen showing a social media post with three short one-line replies stacked beneath it, every word blurred and unreadable, thumb at the edge of the frame, cool screen light, no faces, no lettering"

      - type: image
        from: 8
        slot: 3
        visual_intent: "呼びかけの投稿についた小さな反応の数と、嗤った返信についた大きな反応の数の対比（数字は読めない）"
        cut_reason: "【反応の数の対比】キュー8〜9『呼びかけについた反応は数えるほど』『嗤った返信のほうが何倍も広がっている』。同じ画面の中で、上の投稿には反応アイコンが数個、下の返信には反応アイコンが密集している画"
        gen_prompt: "close-up of a smartphone screen: a post at the top with only two or three tiny reaction icons, and a short reply beneath it crowded with a dense row of reaction icons, numerals and text blurred and unreadable, cool screen light, no faces, no lettering"

      - type: image
        from: 10
        slot: 4
        motion: zoom_out
        visual_intent: "画面の上の指が、何事もなかったように次の投稿へ滑っていく"
        cut_reason: "【指が滑る】キュー10『画面の上の指は、何事もなかったように次の投稿へ滑っていく』。返信欄から引いて、親指がスクロールする手元の画に戻る"
        gen_prompt: "a stranger's thumb scrolling upward across a smartphone screen on a bright commuter train, screen content blurred and unreadable, hand and phone only, no faces, soft daylight, no lettering"

      - type: image
        from: 11
        slot: 5
        visual_intent: "冷笑の定義。本気で何かをしようとする人を、一段高いところから鼻で笑って済ませる態度。スマホを下ろした人の後ろ姿"
        cut_reason: "【冷笑の定義】キュー11〜12『こういう反応を冷笑と呼ぶ』『本気で何かをしようとする人を一段高いところから鼻で笑って済ませる態度』。画面から離れ、車内でスマホを少し下ろした人の後ろ姿で定義文を受ける"
        gen_prompt: "seen from directly behind on a daytime commuter train: the back of a person lowering a smartphone slightly, shoulders relaxed, the screen a plain glowing white rectangle, blurred passengers beyond, no faces, no lettering"

'''

SCENE2 = '''    narration:
      - text: "この態度は近ごろ、ネットでは冷笑系と呼ばれるようになった。"
        pause_after: 0.4
      - text: "だが、冷笑そのものは、新しいものではない。"
        pause_after: 0.4
      - text: "冷笑は、英語でシニシズムという。"
        pause_after: 0.3
      - text: "そしてこの言葉のもとになったのは、およそ2400年前、古代ギリシャにいた哲学者たちだ。"
        pause_after: 0.4
      - text: "ところが彼らは、今の冷笑とは、まるで反対のことをしていた。"
        pause_after: 0.9
      - text: "なぜ人は、冷笑をしてしまうのか。"
        pause_after: 1.0
      - text: "この動画では、古代の哲学者の逸話から、現代の心理学の実験まで、その道筋をたどっていく。"
        pause_after: 0.5
    readings:
      - surface: "冷笑系"
        reading: "レイショウケイ"
      - surface: "冷笑"
        reading: "レイショウ"
    beats:
      - type: image
        from: 1
        slot: 1
        visual_intent: "ネットの返信欄に並ぶ短い言葉（読めない）。冷笑系というラベル"
        cut_reason: "【冷笑系というラベル】キュー1〜2『この態度は近ごろネットでは冷笑系と呼ばれる』『冷笑そのものは新しいものではない』。シーン1の返信欄の画を別角度で引き継ぐ"
        gen_prompt: "a smartphone lying on a cafe table, its screen showing rows of short blurred unreadable reply comments under a post, cool daylight, hand resting beside it, no faces, no lettering"

      - type: image
        from: 3
        slot: 2
        visual_intent: "冷笑＝シニシズム。言葉のもとになった古代ギリシャの哲学者たち。画面が現代から古代の市場へ切り替わる"
        cut_reason: "【シニシズムという言葉の来歴】キュー3〜4『冷笑は英語でシニシズムという』『この言葉のもとになったのは2400年前の古代ギリシャの哲学者たち』。ここで光の温度を暖色へ切り替える"
        gen_prompt: "an empty sunlit ancient Greek marketplace at noon, pale stone paving and sand-colored walls, market stalls with clay pots, warm painterly light, no people, no text, no lettering"

      - type: image
        from: 5
        slot: 3
        visual_intent: "『彼らは今の冷笑とはまるで反対のことをしていた』。同じ古代の市場を保持し、粗末な衣の男の後ろ姿を遠景に置く"
        cut_reason: "【反対のことをしていた】キュー5『ところが彼らは、今の冷笑とはまるで反対のことをしていた』。次章の主人公を遠景で予告する"
        gen_prompt: "a sunlit ancient Greek marketplace at noon seen from a distance, a single small figure in a rough cloak standing alone in the open square among market stalls, seen from behind, warm stone tones, painterly, no faces, no lettering"

      - type: image
        from: 6
        slot: 4
        telop: "なぜ人は、冷笑してしまうのか"
        visual_intent: "問いの提示。同じ古代の市場を静止したまま保持し、問いをtelopで大きく示す"
        cut_reason: "【問いの提示】キュー6〜7『なぜ人は冷笑をしてしまうのか』『この動画では古代の哲学者の逸話から現代の心理学の実験までその道筋をたどる』。画は動かさず、問いの文言はtelopが担う"
        gen_prompt: "a sunlit ancient Greek marketplace at noon seen from a distance, a single small figure in a rough cloak standing alone in the open square among market stalls, seen from behind, warm stone tones, painterly, no faces, no lettering"

'''

s = replace_from_narration(s, 1, SCENE1)
s = replace_from_narration(s, 2, SCENE2)

# scene 3: telop 削除
s = s.replace('        telop: "人間を探している"\n', "")

# scene 8
R8 = {
    '"ここで、冒頭の場面に一度戻ってほしい。"': '"ここで、冒頭の画面に一度戻ってほしい。"',
    '"あなたの指が一瞬止まった投稿は、あなたを責めていただろうか。"': '"意識高いね、と返した人は、あの呼びかけに責められていただろうか。"',
    '"だが、責められるかもしれない、と、あなたの中の何かが予期した。"': '"だが、責められるかもしれない、と、その人の中の何かが予期した。"',
}
for k, v in R8.items():
    assert k in s, k
    s = s.replace(k, v)
a, b = scene_span(s, 8)
chunk = s[a:b]
P_REPLIES = "close-up of a smartphone screen showing a social media post with three short one-line replies stacked beneath it, every word blurred and unreadable, thumb at the edge of the frame, cool screen light, no faces, no lettering"
P_OTS = "over-the-shoulder view on a bright daytime commuter train of a stranger's hand holding a smartphone, thumb resting still on a screen of blurred unreadable replies, no faces, soft window light, documentary still, no lettering"
chunk = re.sub(r'(      - type: image\n        from: 13\n        slot: 6\n.*?gen_prompt: )"[^"]*"', lambda m: m.group(1) + '"' + P_REPLIES + '"', chunk, flags=re.S)
chunk = re.sub(r'(      - type: image\n        from: 15\n        slot: 7\n.*?gen_prompt: )"[^"]*"', lambda m: m.group(1) + '"' + P_OTS + '"', chunk, flags=re.S)
s = s[:a] + chunk + s[b:]

# scene 14
R14 = {
    '"昼の電車で、指が一瞬止まった、あの投稿を思い出してほしい。"': '"昼の電車の、あの画面を思い出してほしい。"',
    '"あの一瞬に、あなたは何かから、自分を守っていた。"': '"意識高いね、と返したその一瞬に、その人は何かから、自分を守っていた。"',
}
for k, v in R14.items():
    assert k in s, k
    s = s.replace(k, v)
old17 = '      - text: "それが分かれば、次の一瞬は、少し違うものになるかもしれない。"\n'
assert old17 in s
s = s.replace(old17, '      - text: "そして同じ一瞬は、たぶん、あなたの中にもある。"\n        pause_after: 0.5\n' + old17)
a, b = scene_span(s, 14)
chunk = s[a:b]
assert "      - type: image\n        from: 18\n        slot: 7" in chunk
chunk = chunk.replace("      - type: image\n        from: 18\n        slot: 7", "      - type: image\n        from: 19\n        slot: 7")
P_OTS2 = "over-the-shoulder view on a bright daytime commuter train of a stranger's hand holding a smartphone, the screen showing a post with short blurred unreadable replies beneath it, no faces, soft window light, documentary still, no lettering"
chunk = re.sub(r'(      - type: image\n        from: 12\n        slot: 5\n.*?gen_prompt: )"[^"]*"', lambda m: m.group(1) + '"' + P_OTS2 + '"', chunk, flags=re.S)
s = s[:a] + chunk + s[b:]

p.write_text(s, encoding="utf-8")
print("ok")
