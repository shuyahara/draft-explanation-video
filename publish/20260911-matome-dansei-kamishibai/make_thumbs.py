# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（"誠実"な男性はモテないのか・紙芝居版, Issue #34）。

サムネ3案（A/B/C）と比較用コンタクトシートを作る。

前作 `publish/20260909-inmu-kamishibai/make_thumbs.py` のフォント・縁取り・配色の
流儀を踏襲しつつ、A案は script_to_video.kamishibai の黒板下地・チョーク文字描画
（render_board_plate / chalk_text_layer / _chalk_font）をそのまま流用して本編と
同じ質感の黒板サムネにする。
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\Users\shuya\Projects\script-to-video\src")

from script_to_video.kamishibai import (
    add_paper_outline,
    chalk_text_layer,
    compute_stage,
    load_sprite,
    render_board_plate,
    _chalk_font,
    CHALK_COLOR,
)
from script_to_video.schema import Kamishibai

OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260911-matome-dansei-kamishibai")
SPRITES = Path(r"C:/Users/shuya/Projects/assets-kamishibai/sprites")
PHOTO_B = Path(r"C:/Users/shuya/Projects/assets-kamishibai/render-assets-matome/scene_01_beat1.jpg")

CFG = Kamishibai()

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")

W, H = 1280, 720

WHITE = (255, 255, 255, 255)
GOLD = (194, 169, 112, 255)  # design-chic-tone.md の金アクセント #C2A970
BLACK_STROKE = (10, 10, 10, 255)
CHALK_RGBA = (*CHALK_COLOR, 255)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def fit_bold_font(text: str, max_width: int, max_height: int, stroke_width: int, max_size: int = 500,
                   font_path: Path = FONT_BOLD) -> ImageFont.FreeTypeFont:
    tmp = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(tmp)
    lo, hi = 10, max_size
    best = ImageFont.truetype(str(font_path), lo)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(str(font_path), mid)
        bbox = draw.textbbox((0, 0), text, font=f, stroke_width=stroke_width)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= max_width and h <= max_height:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def draw_mixed_center(base: Image.Image, segments: list[tuple[str, tuple]], center_x: int, center_y: int,
                       font: ImageFont.FreeTypeFont, stroke_width: int, stroke_fill=BLACK_STROKE) -> None:
    draw = ImageDraw.Draw(base)
    full_text = "".join(t for t, _ in segments)
    bbox_full = draw.textbbox((0, 0), full_text, font=font, stroke_width=stroke_width)
    full_w = bbox_full[2] - bbox_full[0]
    h = bbox_full[3] - bbox_full[1]
    x = center_x - full_w / 2 - bbox_full[0]
    y = center_y - h / 2 - bbox_full[1]
    for text, color in segments:
        draw.text((x, y), text, font=font, fill=color, stroke_width=stroke_width, stroke_fill=stroke_fill)
        seg_bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        x += seg_bbox[2] - seg_bbox[0]


def cover_fit(photo: Image.Image, width: int, height: int) -> Image.Image:
    img = photo.convert("RGB")
    w, h = img.size
    target_ratio = width / height
    cur_ratio = w / h
    if cur_ratio > target_ratio:
        new_w = round(h * target_ratio)
        x0 = (w - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, h))
    else:
        new_h = round(w / target_ratio)
        y0 = (h - new_h) // 2
        img = img.crop((0, y0, w, y0 + new_h))
    return img.resize((width, height), Image.LANCZOS).convert("RGBA")


def darken_band(base: Image.Image, y0: int, y1: int, amount: float) -> None:
    """base の y0〜y1 帯だけを黒く沈める（グラデーションなし・単純帯）。"""
    veil = Image.new("RGBA", (base.width, y1 - y0), (0, 0, 0, round(255 * amount)))
    base.alpha_composite(veil, (0, y0))


def load_puppet(character_dir: str, expression: str, target_height: int) -> Image.Image:
    """立ち絵を読み、余白をトリムして目標高にリサイズし、白い縁を付ける。"""
    raw = load_sprite(SPRITES / character_dir, expression)
    bbox = raw.getbbox()
    cropped = raw.crop(bbox) if bbox else raw
    scale = target_height / cropped.height
    resized = cropped.resize((max(1, round(cropped.width * scale)), target_height), Image.LANCZOS)
    outline_px = round(CFG.puppet_outline_px * H / 1080)
    return add_paper_outline(resized, outline_px)


def paste(base: Image.Image, layer: Image.Image, x: float, y: float) -> None:
    base.paste(layer, (round(x), round(y)), layer)


def vertical_gradient(width: int, height: int, top: tuple, bottom: tuple) -> Image.Image:
    grad = Image.new("RGB", (1, height))
    for y in range(height):
        t = y / max(1, height - 1)
        px = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        grad.putpixel((0, y), px)
    return grad.resize((width, height), Image.NEAREST).convert("RGBA")


def chalk_line(base: Image.Image, text: str, center_x: int, center_y: int, size: int,
               color: tuple = CHALK_RGBA) -> None:
    """本編と同じ chalk_text_layer でチョーク文字1行を中央寄せで貼る。"""
    layer = chalk_text_layer(text, _chalk_font(size), color=color[:3])
    base.alpha_composite(layer, (round(center_x - layer.width / 2), round(center_y - layer.height / 2)))


def fit_chalk_size(text: str, max_width: int, max_height: int, max_size: int = 400) -> int:
    tmp = Image.new("L", (10, 10))
    draw = ImageDraw.Draw(tmp)
    lo, hi = 10, max_size
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        f = _chalk_font(mid)
        bbox = draw.textbbox((0, 0), text, font=f)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= max_width and h <= max_height:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


# ---------------------------------------------------------------------------
# A: 黒板（本編と同じ下地）＋ めたん serious ＋ チョーク文字2行
# ---------------------------------------------------------------------------

def make_thumb_a() -> Image.Image:
    stage = compute_stage(W, H, CFG)
    bg = render_board_plate(stage, CFG).convert("RGBA")
    bl, bt, br, bb = stage.board_rect

    # 右上: 小さく「誠実なのに、なぜ？」
    # チョーク書体（UDDigiKyokashoN）は半角ダブルクオートが開閉とも同じ字形になり
    # 引用符に見えないため、鉤括弧に置き換える。
    small_text = "「誠実」なのに、なぜ？"
    small_size = fit_chalk_size(small_text, max_width=round((br - bl) * 0.42), max_height=round((bb - bt) * 0.10))
    small_x = br - round((br - bl) * 0.02)
    small_layer = chalk_text_layer(small_text, _chalk_font(small_size), color=CHALK_COLOR)
    bg.alpha_composite(small_layer, (small_x - small_layer.width, bt + round((bb - bt) * 0.05)))

    # 左: めたん serious（頭〜胸まで、板の下端に立つ）
    puppet_zone_right = bl + round((br - bl) * 0.42)
    puppet_h = round((bb - bt) * 0.98)
    metan = load_puppet("metan", "serious", puppet_h)
    metan_cx = bl + round((puppet_zone_right - bl) * 0.52)
    paste(bg, metan, metan_cx - metan.width / 2, bb - metan.height)

    # 中央〜右: 大きく2行「負けているのは、」「優しさではない」
    text_zone_left = puppet_zone_right + round((br - bl) * 0.02)
    text_zone_w = br - text_zone_left - round((br - bl) * 0.03)
    text_cx = text_zone_left + text_zone_w // 2
    line1, line2 = "負けているのは、", "優しさではない"
    size1 = fit_chalk_size(line1, max_width=text_zone_w, max_height=round((bb - bt) * 0.30))
    size2 = fit_chalk_size(line2, max_width=text_zone_w, max_height=round((bb - bt) * 0.30))
    size = min(size1, size2)
    f = _chalk_font(size)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    line_h = probe.textbbox((0, 0), line1, font=f)[3]
    gap = round(line_h * 0.18)
    board_cy = (bt + bb) // 2
    y1 = board_cy - line_h / 2 - gap / 2
    y2 = board_cy + line_h / 2 + gap / 2
    chalk_line(bg, line1, text_cx, round(y1), size)
    chalk_line(bg, line2, text_cx, round(y2), size)

    return bg


# ---------------------------------------------------------------------------
# B: S1のスマホ手元写真（暗め）＋ 上下2行の文言 ＋ 両端に頭肩だけのめたん・ずんだもん
# ---------------------------------------------------------------------------

def make_thumb_b() -> Image.Image:
    photo = Image.open(PHOTO_B)
    bg = cover_fit(photo, W, H)
    darken_band(bg, 0, round(H * 0.30), 0.35)
    darken_band(bg, round(H * 0.66), H, 0.35)

    f1 = fit_bold_font("誠実なのに、モテない", max_width=round(W * 0.90), max_height=round(H * 0.19), stroke_width=9)
    draw_mixed_center(bg, [("誠実なのに、モテない", WHITE)], W // 2, round(H * 0.16), f1, stroke_width=9)

    # 頭肩だけの立ち絵を画面隅に小さく寄せ、中央の帯を文言専用にする（重なり回避）。
    puppet_h = round(H * 0.46)
    metan = load_puppet("metan", "explain", puppet_h)
    zun = load_puppet("zundamon", "normal", puppet_h)
    head_top_y = H - round(puppet_h * 0.62)
    metan_cx = round(W * 0.075)
    zun_cx = round(W * 0.925)
    paste(bg, metan, metan_cx - metan.width / 2, head_top_y)
    paste(bg, zun, zun_cx - zun.width / 2, head_top_y)

    f2 = fit_bold_font("誠実さは、伝わるのが遅い", max_width=round(W * 0.66), max_height=round(H * 0.17), stroke_width=9)
    draw_mixed_center(bg, [("誠実さは、伝わるのが遅い", GOLD)], W // 2, round(H * 0.85), f2, stroke_width=9)
    return bg


# ---------------------------------------------------------------------------
# C: 二本のものさし（優しさ＝満・前に出る力＝空欄）＋ ずんだもん confused
# ---------------------------------------------------------------------------

def draw_ruler(base: Image.Image, x_center: int, top_y: int, height: int, width: int, filled: bool,
               fill_color: tuple, label: str, mark: str) -> None:
    draw = ImageDraw.Draw(base)
    x0, x1 = x_center - width // 2, x_center + width // 2
    y1 = top_y + height

    if filled:
        draw.rounded_rectangle([x0, top_y, x1, y1], radius=width // 4, fill=(*fill_color, 255),
                                outline=(255, 255, 255, 255), width=4)
        n_ticks = 8
        for i in range(1, n_ticks):
            ty = top_y + round(height * i / n_ticks)
            draw.line([(x0 + 8, ty), (x1 - 8, ty)], fill=(255, 255, 255, 160), width=3)
    else:
        draw.rounded_rectangle([x0, top_y, x1, y1], radius=width // 4, outline=(255, 255, 255, 220), width=5)
        n_ticks = 8
        for i in range(1, n_ticks):
            ty = top_y + round(height * i / n_ticks)
            dash_w = 10
            xx = x0 + 8
            while xx < x1 - 8:
                draw.line([(xx, ty), (min(xx + dash_w, x1 - 8), ty)], fill=(255, 255, 255, 90), width=3)
                xx += dash_w * 2

    mark_font = fit_bold_font(mark, max_width=width, max_height=round(height * 0.22), stroke_width=6)
    mark_color = fill_color if filled else (255, 255, 255)
    draw_mixed_center(base, [(mark, (*mark_color, 255))], x_center, top_y - round(height * 0.10), mark_font,
                       stroke_width=6)

    label_font = fit_bold_font(label, max_width=round(width * 2.6), max_height=round(height * 0.16), stroke_width=7)
    draw_mixed_center(base, [(label, WHITE)], x_center, y1 + round(height * 0.14), label_font, stroke_width=7)


def make_thumb_c() -> Image.Image:
    bg = vertical_gradient(W, H, (16, 22, 20), (34, 44, 40))

    title1 = '"誠実"に入っていない、'
    title2 = "もう一つの目盛り"
    f1 = fit_bold_font(title1, max_width=round(W * 0.92), max_height=round(H * 0.13), stroke_width=8)
    f2 = fit_bold_font(title2, max_width=round(W * 0.92), max_height=round(H * 0.13), stroke_width=8)
    size = min(f1.size, f2.size)
    f1 = ImageFont.truetype(str(FONT_BOLD), size)
    f2 = f1
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    line_h = probe.textbbox((0, 0), title1, font=f1, stroke_width=8)[3]
    gap = round(line_h * 0.22)
    y1 = round(H * 0.02) + line_h / 2
    y2 = y1 + line_h + gap
    draw_mixed_center(bg, [(title1, WHITE)], W // 2, round(y1), f1, stroke_width=8)
    draw_mixed_center(bg, [(title2, WHITE)], W // 2, round(y2), f2, stroke_width=8)

    ruler_h = round(H * 0.34)
    ruler_w = round(W * 0.09)
    ruler_top = round(H * 0.42)
    left_cx = round(W * 0.34)
    right_cx = round(W * 0.60)
    draw_ruler(bg, left_cx, ruler_top, ruler_h, ruler_w, True, GOLD[:3], "優しさ", "○")
    draw_ruler(bg, right_cx, ruler_top, ruler_h, ruler_w, False, GOLD[:3], "前に出る力", "？")

    zun_h = round(H * 0.42)
    zun = load_puppet("zundamon", "confused", zun_h)
    paste(bg, zun, W - round(W * 0.05) - zun.width, H - zun.height + round(zun.height * 0.06))
    return bg


# ---------------------------------------------------------------------------
# コンタクトシート
# ---------------------------------------------------------------------------

def make_contact_sheet(images: list[Image.Image], labels: list[str]) -> Image.Image:
    n = len(images)
    scale_w = 320
    scale_h = round(H * scale_w / W)
    sheet = Image.new("RGB", (scale_w * n, scale_h), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    label_font = _font(round(scale_h * 0.14))
    for i, (img, label) in enumerate(zip(images, labels)):
        tile = img.convert("RGB").resize((scale_w, scale_h), Image.LANCZOS)
        sheet.paste(tile, (i * scale_w, 0))
        lx, ly = i * scale_w + 8, 6
        draw.text((lx, ly), label, font=label_font, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    return sheet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    images = []
    labels = ["A", "B", "C"]
    for name, fn in [("A", make_thumb_a), ("B", make_thumb_b), ("C", make_thumb_c)]:
        img = fn()
        p = OUT / f"thumb-{name}.png"
        img.convert("RGB").save(p, "PNG", optimize=True)
        print(p)
        images.append(img)

    sheet = make_contact_sheet(images, labels)
    p = OUT / "thumb-contact.jpg"
    sheet.save(p, quality=88)
    print(p)


if __name__ == "__main__":
    main()
