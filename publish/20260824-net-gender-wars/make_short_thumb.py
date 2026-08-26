# -*- coding: utf-8 -*-
"""ショート用サムネイル（short-thumb.png、1080x1920）を合成する使い捨てスクリプト。

ベースは script-to-video/build/net-gender-wars-codex/thumb-base-b.png
（言い合う男女＋中央で首をかしげる人物、1672x941）。横長素材を縦1080x1920へ
トリミングする。9:16の最大幅は元画像の縦941pxからの逆算で529pxしか取れない
（941*9/16≈529）ため、左右の男女の顔まではほぼ入らない
（中央人物を画面中央に置き、できる範囲の縁だけ残す）。
文字は make_thumb05.py の規約を踏襲: Meiryo Bold、白＋ゴールド(#C2A970)、
黒縁取り(stroke_width=10)。中央人物の頭髪トップ(実測 y≈531)に掛からないよう、
文字ブロックはy=40〜470に収める。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(r"C:/Users/shuya/Projects/script-to-video/build/net-gender-wars-codex")
OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260824-net-gender-wars")

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")
W, H = 1080, 1920

GOLD = (194, 169, 112, 255)
WHITE = (255, 255, 255, 255)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def load_cropped_base() -> Image.Image:
    img = Image.open(ASSETS / "thumb-base-b.png").convert("RGB")
    w, h = img.size
    target_ratio = W / H
    cw = round(h * target_ratio)
    cx = w // 2
    x0 = cx - cw // 2
    crop = img.crop((x0, 0, x0 + cw, h))
    crop = crop.resize((W, H), Image.LANCZOS)
    return crop.convert("RGBA")


def fit_font_for_lines(lines: list[str], max_width: int, max_size: int = 260) -> ImageFont.FreeTypeFont:
    lo, hi = 10, max_size
    best = _font(lo)
    tmp = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(tmp)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = _font(mid)
        widths = [draw.textbbox((0, 0), line, font=f)[2] for line in lines]
        if max(widths) <= max_width:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def draw_outlined_line(img, text, center_x, top_y, font, fill):
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = center_x - w / 2 - bbox[0]
    y = top_y - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=10, stroke_fill=(0, 0, 0, 255))
    return bbox[3] - bbox[1]


if __name__ == "__main__":
    img = load_cropped_base()

    line1 = "男女論はなぜ"
    line2 = "炎上するのか？"
    font = fit_font_for_lines([line1, line2], max_width=960)

    top_y = 50
    line_gap = 16
    h1 = draw_outlined_line(img, line1, W // 2, top_y, font, WHITE)
    draw_outlined_line(img, line2, W // 2, top_y + h1 + line_gap, font, GOLD)

    out = img.convert("RGB")
    path = OUT / "short-thumb.png"
    out.save(path, "PNG", optimize=True)
    print(f"{path.name}: {path.stat().st_size / 1024:.1f} KB, font size used")

    small = out.resize((270, 480), Image.LANCZOS)
    small.save(path.with_name(path.stem + "_check.png"))
