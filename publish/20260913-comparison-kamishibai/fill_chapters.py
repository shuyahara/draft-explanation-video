# -*- coding: utf-8 -*-
"""レンダ出力の timeline.json からチャプター行を作り、description-v1.txt の __CHAPTERS__ を埋めて
description-v2.txt に書き出す。章名は timeline.json の scene.chapter_title（章カードの文言）を使い、
章カードのないシーンは OVERRIDE の短い見出しで補う（YouTube の章は最初が 0:00・3 章以上・各 10 秒以上）。
全 9 シーンをそれぞれ 1 章にする（前作 matome-dansei と同じ粒度）。

  .venv\\Scripts\\python.exe publish/20260913-comparison-kamishibai/fill_chapters.py D:/script-to-video-build/comparison-v1
"""
import io
import json
import sys
from pathlib import Path

OVERRIDE = {  # v5（2026-09-15）: S1・S2 統合で 9 シーン
    1: "同期の昇進を見た夜",
    5: "SNS は相手を選ばせない",
    7: "やめれば解決か",
    9: "なぜ比べてしまうのか",
}
out_dir = Path(sys.argv[1])
here = Path(__file__).parent
tl = json.load(io.open(out_dir / "timeline.json", encoding="utf-8"))
rows = []
for e in tl["entries"]:
    if e.get("kind") != "scene":
        continue
    t = int(e["start"])
    title = e.get("chapter_title") or OVERRIDE.get(e["scene_id"], e["title"].split("（")[0])
    rows.append(f"{t // 60}:{t % 60:02d} {title}")
chapters = "\n".join(rows)
src = io.open(here / "description-v1.txt", encoding="utf-8").read()
assert "__CHAPTERS__" in src
dst = src.replace("__CHAPTERS__", chapters)
io.open(here / "description-v2.txt", "w", encoding="utf-8", newline="\n").write(dst)
print(chapters)
print("bytes:", len(dst.encode("utf-8")), "total:", tl["total_duration"])
