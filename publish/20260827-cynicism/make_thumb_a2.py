# -*- coding: utf-8 -*-
"""thumb-A の文言を「なぜ冷笑してしまうのか？」に変更（2026-08-28 ユーザー指示）。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import make_thumbs as mt

# 案1: 右上の空きに 3 行（5 文字幅）
img = mt.load_base("base-A.png")
bbox, fs = mt.draw_panel_caption(
    img, [("なぜ冷笑", mt.GOLD), ("してしまう", mt.WHITE), ("のか？", mt.WHITE)],
    center=(1020, 240), max_width=430, max_line_height=120, line_gap=8)
print("A-3line bbox", bbox, "font", fs)
mt.save(img, "thumb-A.png")

# 案2: 右下の空きに 2 行（6 文字幅）
img = mt.load_base("base-A.png")
bbox, fs = mt.draw_panel_caption(
    img, [("なぜ冷笑して", mt.GOLD), ("しまうのか？", mt.WHITE)],
    center=(995, 560), max_width=480, max_line_height=120, line_gap=8)
print("A-2line bbox", bbox, "font", fs)
mt.save(img, "thumb-A-alt.png")
