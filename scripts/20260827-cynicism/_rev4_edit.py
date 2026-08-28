# -*- coding: utf-8 -*-
"""rev4: 2回目の GPT レビュー（rev3 に対する）から採用した 7 件。セグメント数は変えない。
引数 --yaml を付けたときだけ YAML にも適用する（レンダ中は md/html のみ）。"""
import sys
from pathlib import Path

R = [
    ("冷笑は、英語でシニシズムという。", "英語では、こうした態度をシニシズムと呼ぶ。"),
    ("神殿のそばに置かれた大きな甕の中で寝起きし", "神殿のそばに置かれた、大きな素焼きの甕の中で寝起きし"),
    ("津田氏が例に挙げたのは、ある広告ポスターをめぐる論争だった。", "津田氏が例に挙げたのは、アニメ調の女性キャラクターを使った献血ポスターをめぐる論争だった。"),
    ("そして、その否定の強さは、ある予期と比例していた。", "そして、否定が強い人ほど、ある予期を抱いていた。"),
    ("似た誰かが、先に行った。", "自分と似た立場の誰かが、先に行った。"),
    ("本気で何かを変えようとする人は、しばしば後者に置かれる。", "本気で何かを変えようとする人は、成果が見えにくいぶん、しばしば後者に置かれる。"),
    ("日本は不信の国ではなく、無力感の国なのだ。", "日本で目立つのは、不信よりも、無力感なのだ。"),
]
files = [
    Path(r"C:\Users\shuya\Projects\draft-explanation-video\scripts\20260827-cynicism\20260827-cynicism.md"),
    Path(r"C:\Users\shuya\AppData\Local\Temp\claude\c--Users-shuya-Projects-draft-explanation-video\66cfcae9-e0f2-4863-a717-3e5d76ee60e1\scratchpad\cynicism-script.html"),
]
if "--yaml" in sys.argv:
    files.append(Path(r"C:\Users\shuya\Projects\draft-explanation-video\scripts\20260827-cynicism\20260827-cynicism.yaml"))
for f in files:
    s = f.read_text(encoding="utf-8")
    hits = []
    for a, b in R:
        n = s.count(a)
        if n:
            s = s.replace(a, b)
        hits.append(n)
    f.write_text(s, encoding="utf-8")
    print(f.name, hits)
