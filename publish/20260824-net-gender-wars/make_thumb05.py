# -*- coding: utf-8 -*-
"""thumb-05: ベースB（首をかしげる人物）に大きめの2行コピー
「男女論はなぜ／炎上するのか？」を合成する（2026-08-26 ユーザー指定）。

パネルは敷かず、太い黒縁取りの直書きで文字を大きく取る（make_thumbs.py の規約を踏襲:
Meiryo Bold、白＋ゴールド #C2A970）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).parent))
from make_thumbs import load_base, _font, save, make_check, GOLD, WHITE

W, H = 1280, 720


def draw_outlined_line(img, text, center_x, top_y, font_size, fill):
    draw = ImageDraw.Draw(img)
    font = _font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = center_x - w / 2 - bbox[0]
    y = top_y - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=10, stroke_fill=(0, 0, 0, 255))
    return bbox[3] - bbox[1]


if __name__ == "__main__":
    img = load_base("thumb-base-b.png")
    # 1行目（白）: 上端の暗部帯。2行目（金）: その下。中央人物の頭頂（y≈190）に掛けない
    h1 = draw_outlined_line(img, "男女論はなぜ", 640, 18, 96, WHITE)
    draw_outlined_line(img, "炎上するのか？", 640, 18 + h1 + 12, 96, GOLD)
    p = save(img, "thumb-05.png")
    make_check(p)
    print(f"{p.name}: {p.stat().st_size/1024:.1f} KB")
