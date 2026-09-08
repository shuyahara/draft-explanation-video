# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（男女論・紙芝居版）。

前作（ルッキズム・紙芝居版 `publish/20260906-lookism-kamishibai/make_thumbs.py`）の
K 案の構図（写真全面＋暗幕＋人形は下端から大きく覗く＋見出しは白1行目・黄色2行目）を
そのまま踏襲する。文字・キャラの大きさと配置は同一。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\shuya\Projects\script-to-video\src")

from PIL import Image, ImageDraw, ImageFont

from script_to_video.kamishibai import add_paper_outline, compute_stage, load_sprite
from script_to_video.schema import Kamishibai

OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260907-gender-wars-kamishibai")
SPRITES = Path(r"C:/Users/shuya/Projects/assets-kamishibai/sprites")
PHOTOS = Path(r"C:/Users/shuya/Projects/assets-kamishibai/photos/candidates-genderwars")

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")

W, H = 1280, 720

WHITE = (255, 255, 255, 255)
YELLOW = (247, 226, 122, 255)
BLACK_STROKE = (10, 10, 10, 255)

CFG = Kamishibai()


def load_puppet(character_dir: str, expression: str, target_height: int) -> Image.Image:
    raw = load_sprite(SPRITES / character_dir, expression)
    bbox = raw.getbbox()
    cropped = raw.crop(bbox) if bbox else raw
    scale = target_height / cropped.height
    resized = cropped.resize((max(1, round(cropped.width * scale)), target_height), Image.LANCZOS)
    outline_px = round(CFG.puppet_outline_px * H / 1080)
    return add_paper_outline(resized, outline_px)


def paste(base: Image.Image, layer: Image.Image, x: int, y: int) -> None:
    base.paste(layer, (round(x), round(y)), layer)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def fit_bold_font(text: str, max_width: int, max_height: int, stroke_width: int, max_size: int = 500) -> ImageFont.FreeTypeFont:
    tmp = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(tmp)
    lo, hi = 10, max_size
    best = _font(lo)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = _font(mid)
        bbox = draw.textbbox((0, 0), text, font=f, stroke_width=stroke_width)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= max_width and h <= max_height:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def draw_bold_center(base, text, center_x, center_y, font, fill, stroke_width, stroke_fill=BLACK_STROKE):
    draw = ImageDraw.Draw(base)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = center_x - w / 2 - bbox[0]
    y = center_y - h / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


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


def darken(base: Image.Image, amount: float) -> None:
    veil = Image.new("RGBA", base.size, (0, 0, 0, round(255 * amount)))
    base.alpha_composite(veil)


def draw_headline(base: Image.Image, center_x: int, line1: str, line2: str) -> None:
    f1 = fit_bold_font(line1, max_width=round(W * 0.90), max_height=round(H * 0.185), stroke_width=8)
    draw_bold_center(base, line1, center_x, round(H * 0.30), f1, WHITE, stroke_width=8)
    f2 = fit_bold_font(line2, max_width=round(W * 0.90), max_height=round(H * 0.20), stroke_width=10)
    draw_bold_center(base, line2, center_x, round(H * 0.545), f2, YELLOW, stroke_width=10)


def place_peeking_puppets(base: Image.Image, metan_expr: str, zun_expr: str) -> None:
    stage = compute_stage(W, 900, CFG)
    bl, _bt, br, _bb = stage.board_rect
    board_w = br - bl
    metan = load_puppet("metan", metan_expr, round(H * 1.30))
    zun = load_puppet("zundamon", zun_expr, round(H * 1.30))
    visible_h = round(H * 0.40)
    metan_cx = bl + round(board_w * 0.22)
    zun_cx = br - round(board_w * 0.22)
    top_y = H - visible_h
    paste(base, metan, metan_cx - metan.width / 2, top_y)
    paste(base, zun, zun_cx - zun.width / 2, top_y)


def make_thumb(photo_path: Path, darken_amount: float, line1: str, line2: str,
               metan_expr: str = "smile", zun_expr: str = "surprised") -> Image.Image:
    bg = cover_fit(Image.open(photo_path), W, H)
    darken(bg, darken_amount)
    place_peeking_puppets(bg, metan_expr, zun_expr)
    draw_headline(bg, W // 2, line1, line2)
    return bg


def make_contact_sheet(images: list[Image.Image]) -> Image.Image:
    n = len(images)
    scale_w = W // n
    scale_h = round(H * scale_w / W)
    sheet = Image.new("RGB", (scale_w * n, scale_h), (0, 0, 0))
    for i, img in enumerate(images):
        sheet.paste(img.convert("RGB").resize((scale_w, scale_h), Image.LANCZOS), (i * scale_w, 0))
    return sheet


# A: 暗い部屋のスマホの光。冒頭の場面そのもの。問いをそのまま出す
def make_thumb_a() -> Image.Image:
    return make_thumb(
        PHOTOS / "bedroom-phone-light" / "bedroom-phone-light-1.jpg",
        darken_amount=0.22,
        line1="男女論はなぜ",
        line2="炎上するのか？",
        metan_expr="serious", zun_expr="confused",
    )


# B: コメント欄をスクロールする手元。動画最大の意外な数字を出す
def make_thumb_b() -> Image.Image:
    return make_thumb(
        PHOTOS / "comment-scroll" / "comment-scroll-1.jpg",
        darken_amount=0.38,
        line1="書いているのは",
        line2="たった0.5％",
        metan_expr="smug", zun_expr="surprised",
    )


# C: 人混みの遠景（ブレ）。結論側を出す
def make_thumb_c() -> Image.Image:
    return make_thumb(
        PHOTOS / "crowd-distant" / "crowd-distant-3.jpg",
        darken_amount=0.32,
        line1="憎み合っているのは",
        line2="誰なのか",
        metan_expr="serious", zun_expr="thinking",
    )


# D: 仕組みを出す案（v4 で主軸を「燃えやすい言葉 × 全員が当事者」に据え直したため。0.5% の B は主軸とずれる）
def make_thumb_d() -> Image.Image:
    return make_thumb(
        PHOTOS / "comment-scroll" / "comment-scroll-1.jpg",
        darken_amount=0.38,
        line1="男女論が燃えるのは",
        line2="憎しみのせいじゃない",
        metan_expr="serious", zun_expr="surprised",
    )


# E/F: 背景を「男女が直接言い合っている」生成イラストに（2026-09-08 公開後のユーザー指示）。文言は A と同じ
GEN = Path(r"D:/script-to-video-build/genderwars-assets-codex")


def make_thumb_e() -> Image.Image:
    return make_thumb(
        GEN / "thumb_argue_1.png",
        darken_amount=0.30,
        line1="男女論はなぜ",
        line2="炎上するのか？",
        metan_expr="serious", zun_expr="confused",
    )


def make_thumb_f() -> Image.Image:
    return make_thumb(
        GEN / "thumb_argue_2.png",
        darken_amount=0.35,
        line1="男女論はなぜ",
        line2="炎上するのか？",
        metan_expr="serious", zun_expr="surprised",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = []
    for name, fn in [("A", make_thumb_a), ("B", make_thumb_b), ("C", make_thumb_c), ("D", make_thumb_d), ("E", make_thumb_e), ("F", make_thumb_f)]:
        img = fn()
        p = OUT / f"thumb-{name}.png"
        img.convert("RGB").save(p, "PNG", optimize=True)
        print(p)
        images.append(img)
    sheet = make_contact_sheet(images)
    p = OUT / "thumb-contact.jpg"
    sheet.save(p, quality=88)
    print(p)


if __name__ == "__main__":
    main()
