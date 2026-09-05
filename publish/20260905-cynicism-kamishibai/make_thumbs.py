# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（冷笑・紙芝居版）。

前作（ドパガキ・紙芝居版 `publish/20260904-dopagaki-kamishibai/make_thumbs.py`）の H 案
（写真全面＋暗幕＋画面下端から人形の顔がニュッと覗く配置）をそのまま踏襲する。文字は
「なぜ人は」「冷笑してしまうのか？」の2行固定で、見出しの縦位置・サイズ算出は同スクリプトの
C 案（`make_thumb_c`）の白1行目＋黄色2行目の構図をそのまま流用する（H 案の「なぜXXXに」型の
分割見出しは今回の文言に合わないため使わない）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\shuya\Projects\script-to-video\src")

from PIL import Image, ImageDraw, ImageFont

from script_to_video.kamishibai import (
    add_paper_outline,
    compute_stage,
    load_sprite,
)
from script_to_video.schema import Kamishibai

OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260905-cynicism-kamishibai")
SPRITES = Path(r"C:/Users/shuya/Projects/assets-kamishibai/sprites")
PHOTOS = Path(r"C:/Users/shuya/Projects/assets-kamishibai/render-assets-cynicism")

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")

W, H = 1280, 720

WHITE = (255, 255, 255, 255)
YELLOW = (247, 226, 122, 255)  # #F7E27A
BLACK_STROKE = (10, 10, 10, 255)

CFG = Kamishibai()

LINE1 = "なぜ人は"
LINE2 = "冷笑してしまうのか？"


def load_puppet(character_dir: str, expression: str, target_height: int) -> Image.Image:
    """立ち絵1枚を読み込み、指定の表示高さへリサイズ＋紙の白縁を付けて返す（RGBA）。"""

    raw = load_sprite(SPRITES / character_dir, expression)
    bbox = raw.getbbox()
    cropped = raw.crop(bbox) if bbox else raw
    scale = target_height / cropped.height
    resized = cropped.resize((max(1, round(cropped.width * scale)), target_height), Image.LANCZOS)
    outline_px = round(CFG.puppet_outline_px * H / 1080)
    return add_paper_outline(resized, outline_px)


def paste(base: Image.Image, layer: Image.Image, x: int, y: int) -> None:
    """`layer`（RGBA）を `base`（RGBA）へ左上 (x, y) で貼る。キャンバス外へのはみ出しは自動で
    クリップされる（下端を切って半身だけ見せる配置に使う）。"""

    base.paste(layer, (round(x), round(y)), layer)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def fit_bold_font(text: str, max_width: int, max_height: int, stroke_width: int, max_size: int = 500) -> ImageFont.FreeTypeFont:
    """縁取り込みの外接矩形が (max_width, max_height) に収まる最大サイズの太字フォント。"""

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


def draw_bold_center(base: Image.Image, text: str, center_x: int, center_y: int, font: ImageFont.FreeTypeFont,
                      fill: tuple, stroke_width: int, stroke_fill: tuple = BLACK_STROKE) -> tuple[int, int, int, int]:
    """縁取り付きの太字1行を中央揃えで描く。描いた外接矩形 (l, t, r, b) を返す。"""

    draw = ImageDraw.Draw(base)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = center_x - w / 2 - bbox[0]
    y = center_y - h / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
    return (round(x + bbox[0]), round(y + bbox[1]), round(x + bbox[2]), round(y + bbox[3]))


def save(img: Image.Image, name: str) -> Path:
    out = img.convert("RGB")
    path = OUT / name
    out.save(path, "PNG", optimize=True)
    return path


def cover_fit(photo: Image.Image, width: int, height: int) -> Image.Image:
    """写真を (width, height) いっぱいに覆うクロップ＋リサイズ（cover）。RGBA で返す。"""

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
    """`base`（RGBA）全面へ黒の半透明幕を重ねて `amount`（0〜1）だけ暗くする（可読性確保）。"""

    veil = Image.new("RGBA", base.size, (0, 0, 0, round(255 * amount)))
    base.alpha_composite(veil)


def draw_headline(base: Image.Image, center_x: int) -> None:
    """見出し2行を描く（前作 C 案と同じ構図: 白1行目・黄色2行目、中央揃え）。"""

    line1_font = fit_bold_font(LINE1, max_width=round(W * 0.90), max_height=round(H * 0.185), stroke_width=8)
    draw_bold_center(base, LINE1, center_x, round(H * 0.30), line1_font, WHITE, stroke_width=8)

    line2_font = fit_bold_font(LINE2, max_width=round(W * 0.90), max_height=round(H * 0.20), stroke_width=10)
    draw_bold_center(base, LINE2, center_x, round(H * 0.545), line2_font, YELLOW, stroke_width=10)


def place_peeking_puppets(base: Image.Image, metan_expr: str, zun_expr: str) -> None:
    """人形を画面下端から顔＋肩の上あたりだけ覗かせる（前作 H/C 案と同じ半身クリップ配置）。"""

    stage = compute_stage(W, 900, CFG)
    bl, _bt, br, _bb = stage.board_rect
    board_w = br - bl

    metan_h = round(H * 1.30)
    zun_h = round(H * 1.30)
    metan = load_puppet("metan", metan_expr, metan_h)
    zun = load_puppet("zundamon", zun_expr, zun_h)

    visible_h = round(H * 0.40)  # 画面下端から見せたい高さ（顔＋肩まで）
    metan_cx = bl + round(board_w * 0.22)
    zun_cx = br - round(board_w * 0.22)
    top_y = H - visible_h

    paste(base, metan, metan_cx - metan.width / 2, top_y)
    paste(base, zun, zun_cx - zun.width / 2, top_y)


def make_thumb(photo_path: Path, darken_amount: float) -> Image.Image:
    bg = cover_fit(Image.open(photo_path), W, H)
    darken(bg, darken_amount)
    place_peeking_puppets(bg, "smug", "confused")
    draw_headline(bg, W // 2)
    return bg


# ============================================================
# A: 返信欄を見る手元
# ============================================================

def make_thumb_a() -> Image.Image:
    return make_thumb(PHOTOS / "scene_01_beat2.jpg", darken_amount=0.30)


# ============================================================
# B: 腕を組んで椅子にもたれる人
# ============================================================

def make_thumb_b() -> Image.Image:
    return make_thumb(PHOTOS / "scene_06_beat1.jpg", darken_amount=0.35)


# ============================================================
# C: ジェローム「ディオゲネス」(1860, パブリックドメイン)
# ============================================================

def make_thumb_c() -> Image.Image:
    return make_thumb(PHOTOS / "scene_03_beat1.jpg", darken_amount=0.25)


def make_contact_sheet(images: list[Image.Image]) -> Image.Image:
    """3案を横に並べた確認用サムネイルを作る（各画像を1/3幅に縮小）。"""

    scale_w = W // 3
    scale_h = round(H * scale_w / W)
    sheet = Image.new("RGB", (scale_w * 3, scale_h), (0, 0, 0))
    for i, img in enumerate(images):
        small = img.convert("RGB").resize((scale_w, scale_h), Image.LANCZOS)
        sheet.paste(small, (i * scale_w, 0))
    return sheet


if __name__ == "__main__":
    a = make_thumb_a()
    b = make_thumb_b()
    c = make_thumb_c()

    for img, name in ((a, "thumb-A.png"), (b, "thumb-B.png"), (c, "thumb-C.png")):
        path = save(img, name)
        size_kb = path.stat().st_size / 1024
        print(f"{path}: {img.size} mode={img.mode} -> {size_kb:.1f} KB")

    contact = make_contact_sheet([a, b, c])
    contact_path = OUT / "thumb-contact.jpg"
    contact.save(contact_path, "JPEG", quality=90)
    print(f"{contact_path}: {contact.size} -> {contact_path.stat().st_size / 1024:.1f} KB")
