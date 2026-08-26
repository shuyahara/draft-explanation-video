# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト。

ベース画像2枚（Codex CLI経由で生成、script-to-video/build/net-gender-wars-codex/ に配置）に
Pillow でタイポグラフィのみ合成する。フォント・配色は前作
publish/20260819-sns-lookism-v6/make_thumbs.py の規約を踏襲（Meiryo Bold、白+ゴールド#C2A970）。

顔・手・髪の位置はグリッド確認画像（scratchpad/grid_a.png, grid_b.png）で座標を実測して決定した
（詳細は同ディレクトリの thumbnails.md 参照）。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(r"C:/Users/shuya/Projects/script-to-video/build/net-gender-wars-codex")
OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260824-net-gender-wars")

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
    """1文字（「？」等）の実測グリフ高さが target_height に近くなるフォントサイズを探索する。"""
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
    """複数行それぞれが max_width に収まる最大フォントサイズを探索する。"""
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
    """暗いラウンド角パネルを背景に敷いてから、複数行キャプションを中央揃えで描く。"""
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
        radius=14, fill=(5, 5, 8, 165),
    )
    img.alpha_composite(panel)

    cur_y = top
    for text, color, bbox, w, h in metrics:
        x = cx - w / 2 - bbox[0]
        y = cur_y - bbox[1]
        draw.text((x + 3, y + 3), text, font=font, fill=SHADOW)
        draw.text((x, y), text, font=font, fill=color)
        cur_y += h + line_gap


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

    # thumb-01: ベースA + 中央特大「？」（高さ約58%）
    img = load_base("thumb-base-a.png")
    draw_centered_glyph(img, "？", center=(695, 360), target_height=round(H * 0.58))
    outputs.append(save(img, "thumb-01.png"))

    # thumb-02: ベースA + やや小さめ「？」（高さ約42%、やや上寄せ）+ 下部キャプション
    img = load_base("thumb-base-a.png")
    draw_centered_glyph(img, "？", center=(695, 290), target_height=round(H * 0.42))
    draw_panel_caption(
        img,
        [("書き込んでいるのは、0.5%", WHITE)],
        center=(695, 655),
        max_width=520,
        max_line_height=90,
    )
    outputs.append(save(img, "thumb-02.png"))

    # thumb-03: ベースBそのまま（文字なし）
    img = load_base("thumb-base-b.png")
    outputs.append(save(img, "thumb-03.png"))

    # thumb-04: ベースB + 中央人物頭上の空白域に2行キャプション
    img = load_base("thumb-base-b.png")
    draw_panel_caption(
        img,
        [("その対立、", WHITE), ("本物？", GOLD)],
        center=(645, 78),
        max_width=430,
        max_line_height=64,
        line_gap=6,
    )
    outputs.append(save(img, "thumb-04.png"))

    for p in outputs:
        make_check(p)
        size_kb = p.stat().st_size / 1024
        print(f"{p.name}: {size_kb:.1f} KB")
