# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（新規画像生成なし。動画本編で採用済みの生成画像を再利用）。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ASSETS = Path(r"C:/Users/shuya/Projects/script-to-video/build/sns-lookism-v6-assets")
OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260819-sns-lookism-v6")

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")
W, H = 1280, 720

GOLD = (194, 169, 112, 255)
WHITE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 200)


def load_base(name: str) -> Image.Image:
    img = Image.open(ASSETS / name).convert("RGB")
    target_ratio = W / H
    w, h = img.size
    cur_ratio = w / h
    if cur_ratio > target_ratio:
        new_w = round(h * target_ratio)
        x0 = (w - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, h))
    else:
        new_h = round(w / target_ratio)
        y0 = (h - new_h) // 2
        img = img.crop((0, y0, w, y0 + new_h))
    img = img.resize((W, H), Image.LANCZOS)
    return img


def add_gradient_scrim(img: Image.Image, band: str, strength: float = 0.72) -> Image.Image:
    """band: 'top' / 'bottom' / 'left' (黒グラデーションを重ねて文字の可読性を確保)"""
    overlay = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(overlay)
    if band == "top":
        for y in range(H):
            t = max(0.0, 1.0 - y / (H * 0.55))
            a = int(255 * strength * t)
            draw.line([(0, y), (W, y)], fill=a)
    elif band == "bottom":
        for y in range(H):
            t = max(0.0, 1.0 - (H - y) / (H * 0.55))
            a = int(255 * strength * t)
            draw.line([(0, y), (W, y)], fill=a)
    elif band == "left":
        for x in range(W):
            t = max(0.0, 1.0 - x / (W * 0.58))
            a = int(255 * strength * t)
            draw.line([(x, 0), (x, H)], fill=a)
    black = Image.new("RGB", (W, H), (5, 5, 8))
    return Image.composite(black, img, overlay)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def draw_text_shadowed(draw: ImageDraw.ImageDraw, xy, text, font, fill, shadow=SHADOW, offset=4):
    x, y = xy
    draw.text((x + offset, y + offset), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def compose(base_name: str, lines: list[tuple[str, tuple]], scrim: str, anchor: str, out_name: str,
            size_ratio: float = 0.145, line_gap_ratio: float = 0.02, margin_ratio: float = 0.06):
    img = load_base(base_name)
    img = add_gradient_scrim(img, scrim)
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    size = round(H * size_ratio)
    font = _font(size)
    gap = round(H * line_gap_ratio)

    heights = []
    widths = []
    for text, _ in lines:
        bbox = draw.textbbox((0, 0), text, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + gap * (len(lines) - 1)

    margin = round(W * margin_ratio)
    if anchor == "top-left":
        y = round(H * 0.10)
        x_of = lambda w_: margin
    elif anchor == "left-mid":
        y = (H - total_h) // 2
        x_of = lambda w_: margin
    elif anchor == "bottom-left":
        y = H - round(H * 0.10) - total_h
        x_of = lambda w_: margin
    else:
        y = round(H * 0.10)
        x_of = lambda w_: margin

    cy = y
    for (text, color), lh, lw in zip(lines, heights, widths):
        bbox = draw.textbbox((0, 0), text, font=font)
        draw_text_shadowed(draw, (x_of(lw), cy - bbox[1]), text, font, color)
        cy += lh + gap

    out = img.convert("RGB")
    out.save(OUT / out_name, "PNG", optimize=True)
    return OUT / out_name


def make_thumb_small(path: Path):
    img = Image.open(path)
    small = img.resize((320, 180), Image.LANCZOS)
    small.save(path.with_name(path.stem + "_check.png"))


if __name__ == "__main__":
    outputs = []

    outputs.append(compose(
        "scene_01_beat3.png",
        [("なぜ受け入れ", WHITE), ("始めたのか", GOLD)],
        scrim="top",
        anchor="top-left",
        out_name="thumb-01.png",
        size_ratio=0.155,
    ))

    outputs.append(compose(
        "scene_05_beat7.png",
        [("\u201c美人は得\u201dを", WHITE), ("科学する", GOLD)],
        scrim="left",
        anchor="left-mid",
        out_name="thumb-02.png",
        size_ratio=0.145,
    ))

    outputs.append(compose(
        "scene_07_beat6.png",
        [("いつから", WHITE), ("変わった", GOLD)],
        scrim="left",
        anchor="left-mid",
        out_name="thumb-03.png",
        size_ratio=0.105,
        margin_ratio=0.04,
    ))

    outputs.append(compose(
        "scene_08_beat3.png",
        [("写真SNSが", WHITE), ("変えた景色", GOLD)],
        scrim="bottom",
        anchor="bottom-left",
        out_name="thumb-04.png",
        size_ratio=0.155,
    ))

    for p in outputs:
        make_thumb_small(p)
        size_kb = p.stat().st_size / 1024
        print(f"{p.name}: {size_kb:.1f} KB")
