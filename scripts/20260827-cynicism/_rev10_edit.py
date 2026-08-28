# -*- coding: utf-8 -*-
"""rev10: 試写フィードバック（2026-08-28）
- 誤読: 犬→イヌ（S3/S4/S14）、いつの間にか→イツノマニカ（S4）、の方が→ノホウガ（S6/S11）
- 章2・章3 のタイトルを「現代で冷笑が広がる理由」の連番に（視聴者目線で唐突だったため）
- S5 冒頭の 1 文に橋渡しを足す（セグメント数は不変）
"""
import re
from pathlib import Path
import yaml

y = Path("scripts/20260827-cynicism/20260827-cynicism.yaml"); s = y.read_text(encoding="utf-8")
m = Path("scripts/20260827-cynicism/20260827-cynicism.md"); t = m.read_text(encoding="utf-8")
d = Path("publish/20260827-cynicism/description.txt"); dd = d.read_text(encoding="utf-8")

def add_readings(scene_id, pairs):
    """scene の readings: ブロックの先頭に pairs を挿入（readings が無ければ作らない＝assert）"""
    global s
    data = yaml.safe_load(s)
    sc = next(x for x in data["scenes"] if x["id"] == scene_id)
    assert sc.get("readings"), scene_id
    first = sc["readings"][0]
    anchor = f'    readings:\n      - surface: "{first["surface"]}"\n        reading: "{first["reading"]}"\n'
    assert s.count(anchor) == 1, (scene_id, anchor)
    ins = "    readings:\n" + "".join(f'      - surface: "{a}"\n        reading: "{b}"\n' for a, b in pairs)
    s = s.replace(anchor, ins + anchor[len("    readings:\n"):], 1)

add_readings(3, [("犬", "イヌ")])
add_readings(4, [("犬", "イヌ"), ("いつの間にか", "イツノマニカ")])
add_readings(6, [("の方が", "ノホウガ")])
add_readings(11, [("の方が", "ノホウガ")])
add_readings(14, [("犬", "イヌ")])

CH2_OLD, CH2_NEW = "冷笑は、なぜこんなに安いのか", "現代で冷笑が広がる理由① ― 冷笑は、安い"
CH3_OLD, CH3_NEW = "冷笑は、何を守っているのか", "現代で冷笑が広がる理由② ― 冷笑は、何かを守っている"
for old, new in ((CH2_OLD, CH2_NEW), (CH3_OLD, CH3_NEW)):
    assert s.count(f'chapter_title: "{old}"') == 1
    s = s.replace(f'chapter_title: "{old}"', f'chapter_title: "{new}"')
    s = s.replace(f"「{old}」", f"「{new}」")  # 冒頭コメント
    assert t.count(f"- 章タイトル（chapter_title）: {old}") == 1
    t = t.replace(f"- 章タイトル（chapter_title）: {old}", f"- 章タイトル（chapter_title）: {new}")
    assert dd.count(old) == 1
    dd = dd.replace(old, new)

S5_OLD = "手がかりは、冷笑が驚くほど安上がりだという事実にある。"
S5_NEW = "現代で冷笑が広がる理由の、最初の手がかりは、冷笑が驚くほど安上がりだという事実にある。"
assert s.count(f'text: "{S5_OLD}"') == 1 and t.count(S5_OLD) == 1
s = s.replace(f'text: "{S5_OLD}"', f'text: "{S5_NEW}"'); t = t.replace(S5_OLD, S5_NEW)

# 発音メモ
memo_old = "- 発音・ポーズメモ: 「キュオーン」「キュニコス」「スローターダイク」「マゼラ」を `readings` で確定。"
memo_new = memo_old + "「犬」は「イヌ」（「犬のような者たち」が「ケン」と読まれた）、「いつの間にか」は「イツノマニカ」（rev10）。"
assert t.count(memo_old) == 1; t = t.replace(memo_old, memo_new)

y.write_text(s, encoding="utf-8"); m.write_text(t, encoding="utf-8"); d.write_text(dd, encoding="utf-8")
print("rev10 applied")
