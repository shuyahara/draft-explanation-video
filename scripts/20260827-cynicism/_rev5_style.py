# -*- coding: utf-8 -*-
"""rev5: video.style を時代中立にし、現代場面の gen_prompt に present-day の指定を付ける
（video.style の「古代＝石と砂」がすべての生成プロンプトに前置されて現代場面に遺跡が混ざる問題への対処）。"""
import io, re, yaml
from pathlib import Path

p = Path(r"C:\Users\shuya\Projects\draft-explanation-video\scripts\20260827-cynicism\20260827-cynicism.yaml")
s = p.read_text(encoding="utf-8")

# 1. video.style
m = re.search(r'^  style: "(.*)"$', s, re.M)
assert m, "video.style not found"
old_style = m.group(1)
new_style = ("cinematic documentary still, natural light, muted low-contrast palette, shallow depth of field, "
             "painterly warm stone tones only when the scene itself is ancient Greece, cool white daylight and screen glow "
             "for present-day scenes, no text, no lettering")
s = s.replace(m.group(0), f'  style: "{new_style}"')

# 2. modern prompts
ANCIENT = re.compile(r"ancient|greek|macedonian|athens|oil lamp|clay storage jar|delphi|parchment|1970s|poppies|poppy|fox|grapes", re.I)
d = yaml.safe_load(s)
count = 0
for sc in d["scenes"]:
    for b in sc.get("beats", []):
        g = b.get("gen_prompt")
        if not g or ANCIENT.search(g) or "present-day" in g:
            continue
        new = "present-day scene, " + g.rstrip() + ", no ancient architecture, no columns, no ruins, no historical costume"
        n = s.count(f'gen_prompt: "{g}"')
        if n:
            s = s.replace(f'gen_prompt: "{g}"', f'gen_prompt: "{new}"')
            count += n
p.write_text(s, encoding="utf-8")
print("style replaced; modern prompts updated:", count)
