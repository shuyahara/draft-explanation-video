# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（「人はなぜ他人と比べてしまうのか」・紙芝居版, Issue #38）。

サムネ3案（A/B/C）を作る。構図は前作
`publish/20260911-matome-dansei-kamishibai/make_thumbs.py` の D 案
（実写風背景＋人物中央・腰から上＋金の大きな「？」を重ねる＋全幅の上下2帯＋
下端から顔が覗く立ち絵）をそのまま踏襲し、背景3枚・下帯の文言だけを差し替える。

背景は Codex（`tools/codex_imagegen`）で生成した実写調の夜のスマホ場面
（`thumb-bg/orig/bg-{1,2,3}-raw.png`）。生成サイズが 16:9 より縦長（1370x1148 等）
だったため、対称クロップだと髪の生え際が欠けやすい。人物の頭が画面上部に
寄っているため、縦方向のクロップは上を少なく・下（ベッド・膝から下）を
多く取る非対称クロップ（`cover_fit_top_biased`）にしている。
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\Users\shuya\Projects\script-to-video\src")

from script_to_video.kamishibai import (
    add_paper_outline,
    load_sprite,
)
from script_to_video.schema import Kamishibai

OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260913-comparison-kamishibai")
SPRITES = Path(r"C:/Users/shuya/Projects/assets-kamishibai/sprites")
BG_DIR = OUT / "thumb-bg"

CFG = Kamishibai()

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")

W, H = 1280, 720

WHITE = (255, 255, 255, 255)
GOLD = (194, 169, 112, 255)  # design-chic-tone.md の金アクセント #C2A970
GOLD_SEMI = (194, 169, 112, round(255 * 0.85))
BLACK_STROKE = (10, 10, 10, 255)

TITLE_TOP = "なぜ人と比べてしまうのか"

# (背景ファイル, 下帯の文言, 出力ファイル名, めたんの表情, ずんだもんの表情)
VARIANTS = [
    ("bg-1.png", "比較が壊れた二つの理由", "thumb-A.png", "explain", "confused"),
    ("bg-2.png", "比べるのはやめられない", "thumb-B.png", "serious", "sad"),
    ("bg-3.png", "眺める10分が夜に効く", "thumb-C.png", "explain", "thinking"),
]


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


def cover_fit_top_biased(photo: Image.Image, width: int, height: int, top_bias: float = 0.12) -> Image.Image:
    """target アスペクトへクロップする。縦長の元画像を横長へクロップする側では、
    縦方向の削り幅を上下対称ではなく `top_bias`（上に残す割合）で非対称に取り、
    人物の頭頂（画面上部）を残して膝から下を多めに削る。"""
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
        total_remove = h - new_h
        y0 = round(total_remove * top_bias)
        img = img.crop((0, y0, w, y0 + new_h))
    return img.resize((width, height), Image.LANCZOS).convert("RGBA")


def darken_band(base: Image.Image, y0: int, y1: int, amount: float) -> None:
    veil = Image.new("RGBA", (base.width, y1 - y0), (0, 0, 0, round(255 * amount)))
    base.alpha_composite(veil, (0, y0))


def load_puppet(character_dir: str, expression: str, target_height: int) -> Image.Image:
    raw = load_sprite(SPRITES / character_dir, expression)
    bbox = raw.getbbox()
    cropped = raw.crop(bbox) if bbox else raw
    scale = target_height / cropped.height
    resized = cropped.resize((max(1, round(cropped.width * scale)), target_height), Image.LANCZOS)
    outline_px = round(CFG.puppet_outline_px * H / 1080)
    return add_paper_outline(resized, outline_px)


def paste(base: Image.Image, layer: Image.Image, x: float, y: float) -> None:
    base.paste(layer, (round(x), round(y)), layer)


def make_thumb(bg_path: Path, subtitle: str, metan_expr: str, zun_expr: str) -> Image.Image:
    photo = Image.open(bg_path)
    bg = cover_fit_top_biased(photo, W, H)

    # 上下の暗化帯は全幅（人物にも掛かるが、文言を読ませるための帯なので許容）。
    darken_band(bg, 0, round(H * 0.24), 0.42)
    darken_band(bg, round(H * 0.78), H, 0.42)

    # 中央やや下寄り（y=58%）に大きな金色半透明の「？」（高さ画面の42%）。
    # 人物の目はおおむね画面上部28〜33%あたりに来るため、マーク上端
    # （58%-21%=37%）が目より下に来るよう中心を下げ、目にはかからないようにする。
    mark_h = round(H * 0.42)
    mark_font = fit_bold_font("？", max_width=round(W * 0.55), max_height=mark_h, stroke_width=20)
    draw_mixed_center(bg, [("？", GOLD_SEMI)], W // 2, round(H * 0.58), mark_font, stroke_width=20)

    # 立ち絵: 「下端から顔が覗く」配置。文言より先に貼り、下帯の文言を
    # 立ち絵の上に重ねて描くことで（後述）、文字が立ち絵に隠れないようにする。
    puppet_h = round(H * 0.65)
    metan = load_puppet("metan", metan_expr, puppet_h)
    zun = load_puppet("zundamon", zun_expr, puppet_h)
    peek_top_y = H - round(puppet_h * 0.5)
    metan_cx = round(W * 0.12)
    zun_cx = round(W * 0.88)
    paste(bg, metan, metan_cx - metan.width / 2, peek_top_y)
    paste(bg, zun, zun_cx - zun.width / 2, peek_top_y)

    # 上段（最上部の全幅帯）: 白文字・共通の問い
    f1 = fit_bold_font(TITLE_TOP, max_width=round(W * 0.92), max_height=round(H * 0.16), stroke_width=8)
    draw_mixed_center(bg, [(TITLE_TOP, WHITE)], W // 2, round(H * 0.10), f1, stroke_width=8)

    # 下段（最下部の全幅帯）: 金文字・案ごとの副題。立ち絵の上に重ねて描く
    # （幅は立ち絵の間に収まる 0.66W を上限にし、それでも重なる分は立ち絵より
    # 前面に出して文字を隠さない）。
    f2 = fit_bold_font(subtitle, max_width=round(W * 0.66), max_height=round(H * 0.14), stroke_width=9)
    draw_mixed_center(bg, [(subtitle, GOLD)], W // 2, round(H * 0.90), f2, stroke_width=9)

    return bg


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
    labels = []
    for bg_name, subtitle, out_name, metan_expr, zun_expr in VARIANTS:
        img = make_thumb(BG_DIR / bg_name, subtitle, metan_expr, zun_expr)
        p = OUT / out_name
        img.convert("RGB").save(p, "PNG", optimize=True)
        print(p)
        images.append(img)
        labels.append(out_name.replace("thumb-", "").replace(".png", ""))

    sheet = make_contact_sheet(images, labels)
    p = OUT / "thumb-contact.jpg"
    sheet.save(p, quality=88)
    print(p)


if __name__ == "__main__":
    main()
