# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（冷笑動画）。

ベース画像3枚（Codex CLI経由で生成、script-to-video/build/cynicism-thumb/ に配置）に
Pillow でタイポグラフィのみ合成する。フォント・配色は前作
publish/20260824-net-gender-wars/make_thumbs.py の規約を踏襲（Meiryo Bold、白+ゴールド#C2A970）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(r"C:/Users/shuya/Projects/script-to-video/build/cynicism-thumb")
OUT = Path(r"C:/Users/shuya/Projects/script-to-video/build/cynicism-thumb")

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")
W, H = 1280, 720

GOLD = (194, 169, 112, 255)
WHITE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 220)


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
    return img.convert("RGBA")


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def fit_font_for_height(text: str, target_height: int, max_size: int = 900) -> ImageFont.FreeTypeFont:
    lo, hi = 10, max_size
    best = _font(lo)
    tmp = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(tmp)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = _font(mid)
        bbox = draw.textbbox((0, 0), text, font=f)
        h = bbox[3] - bbox[1]
        if h <= target_height:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def fit_font_for_lines(lines: list[str], max_width: int, max_line_height: int, max_size: int = 300) -> ImageFont.FreeTypeFont:
    lo, hi = 10, max_size
    best = _font(lo)
    tmp = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(tmp)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = _font(mid)
        widths = []
        heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=f)
            widths.append(bbox[2] - bbox[0])
            heights.append(bbox[3] - bbox[1])
        if max(widths) <= max_width and max(heights) <= max_line_height:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def draw_centered_glyph(img: Image.Image, text: str, center: tuple[int, int], target_height: int,
                         fill=GOLD, stroke_width: int = 8, stroke_fill=(0, 0, 0, 255)):
    draw = ImageDraw.Draw(img)
    font = fit_font_for_height(text, target_height)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    cx, cy = center
    x = cx - w / 2 - bbox[0]
    y = cy - h / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
    return bbox, (x, y), font


def draw_panel_caption(img: Image.Image, lines: list[tuple[str, tuple]], center: tuple[int, int],
                        max_width: int, max_line_height: int, line_gap: int = 8, pad: int = 18):
    draw = ImageDraw.Draw(img)
    texts = [t for t, _ in lines]
    font = fit_font_for_lines(texts, max_width, max_line_height)

    metrics = []
    for text, color in lines:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        metrics.append((text, color, bbox, w, h))

    total_h = sum(m[4] for m in metrics) + line_gap * (len(metrics) - 1)
    block_w = max(m[3] for m in metrics)

    cx, cy = center
    top = cy - total_h / 2

    panel = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle(
        [cx - block_w / 2 - pad, top - pad, cx + block_w / 2 + pad, top + total_h + pad],
        radius=14, fill=(5, 5, 8, 175),
    )
    img.alpha_composite(panel)

    cur_y = top
    for text, color, bbox, w, h in metrics:
        x = cx - w / 2 - bbox[0]
        y = cur_y - bbox[1]
        draw.text((x + 3, y + 3), text, font=font, fill=SHADOW)
        draw.text((x, y), text, font=font, fill=color)
        cur_y += h + line_gap

    return (cx - block_w / 2 - pad, top - pad, cx + block_w / 2 + pad, top + total_h + pad), font.size


def draw_outlined_line(img, text, center_x, top_y, font_size, fill):
    draw = ImageDraw.Draw(img)
    font = _font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = center_x - w / 2 - bbox[0]
    y = top_y - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=10, stroke_fill=(0, 0, 0, 255))
    return bbox[3] - bbox[1]


def save(img: Image.Image, out_name: str) -> Path:
    out = img.convert("RGB")
    path = OUT / out_name
    out.save(path, "PNG", optimize=True)
    return path


def make_check(path: Path):
    img = Image.open(path)
    small = img.resize((320, 180), Image.LANCZOS)
    small.save(path.with_name(path.stem + "_check.png"))


if __name__ == "__main__":
    outputs = []

    # thumb-A: ベースA（電車内でスマホを見る後ろ姿）+ 右側の空きに2行「なぜ / 嗤う？」
    img = load_base("base-A.png")
    bbox, font_size = draw_panel_caption(
        img,
        [("なぜ", WHITE), ("嗤う？", GOLD)],
        center=(1070, 260),
        max_width=340,
        max_line_height=130,
        line_gap=10,
    )
    print("A panel bbox", bbox, "font", font_size)
    outputs.append(save(img, "thumb-A.png"))

    # thumb-B: ベースB（街頭で一人語る人物）+ 下部パネルに3行「本気は / なぜ / 笑われる」
    img = load_base("base-B.png")
    bbox, font_size = draw_panel_caption(
        img,
        [("本気は", WHITE), ("なぜ", WHITE), ("笑われる", GOLD)],
        center=(680, 581),
        max_width=560,
        max_line_height=60,
        line_gap=8,
    )
    print("B panel bbox", bbox, "font", font_size)
    outputs.append(save(img, "thumb-B.png"))

    # thumb-C: ベースC（古代の柱と現代の街）+ 右上の空（夕景）に2行「冷笑 / 2400年の系譜」
    img = load_base("base-C.png")
    bbox, font_size = draw_panel_caption(
        img,
        [("冷笑", GOLD), ("2400年の系譜", WHITE)],
        center=(970, 150),
        max_width=560,
        max_line_height=100,
        line_gap=8,
    )
    print("C panel bbox", bbox, "font", font_size)
    outputs.append(save(img, "thumb-C.png"))

    # thumb-C2: ベースC + 右上の空に金色の特大「？」のみ
    img = load_base("base-C.png")
    bbox2, pos, font = draw_centered_glyph(img, "？", center=(970, 150), target_height=260)
    print("C2 glyph bbox", bbox2)
    outputs.append(save(img, "thumb-C2.png"))

    for p in outputs:
        make_check(p)
        size_kb = p.stat().st_size / 1024
        print(f"{p.name}: {size_kb:.1f} KB")
