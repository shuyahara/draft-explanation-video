# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（ドパガキ動画）。

ベース画像（Codex CLI経由で生成、script-to-video/build/dopagaki-assets-codex/ に配置）に
Pillow でタイポグラフィのみ合成する。フォント・配色・パネル演出は前作
publish/20260827-cynicism/make_thumbs.py の規約を踏襲（Meiryo Bold、白+ゴールド#C2A970、
半透明の黒パネルで可読性確保）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(r"C:/Users/shuya/Projects/script-to-video/build/dopagaki-assets-codex")
OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260831-dopagaki")

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

    # thumb-A: 夜、布団の中でスマホの光に照らされる人物 + 右上に3行「なぜドパガキに / なってしまう / のか？」
    img = load_base("scene_01_beat1.png")
    bbox, font_size = draw_panel_caption(
        img,
        [("なぜドパガキに", GOLD), ("なってしまう", WHITE), ("のか？", WHITE)],
        center=(970, 168),
        max_width=560,
        max_line_height=100,
        line_gap=8,
    )
    print("A panel bbox", bbox, "font", font_size)
    outputs.append(save(img, "thumb-A.png"))

    for p in outputs:
        make_check(p)
        size_kb = p.stat().st_size / 1024
        print(f"{p.name}: {size_kb:.1f} KB")
