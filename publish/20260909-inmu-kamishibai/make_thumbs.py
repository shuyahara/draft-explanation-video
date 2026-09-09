# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（淫夢・紙芝居版, Issue #32）。

- 元画像（バストアップ写真）の目に黒帯を入れた画像を作る（本編・サムネ共用）。
- サムネ3案（A/B/C）と比較用コンタクトシートを作る。

前作 `publish/20260907-gender-wars-kamishibai/make_thumbs.py` のフォント・縁取り・
配色（白＋強調イエロー、黒縁）の流儀を踏襲する。ただし本作は紙芝居キャラを使わず、
写真（目線に黒帯）を主役にした構図なので、合成ロジックは新規に書く。
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\Users\shuya\Projects\script-to-video\src")

from script_to_video.kamishibai import add_paper_outline, load_sprite
from script_to_video.schema import Kamishibai

SOURCE_IMG = Path(
    r"C:/Users/shuya/Projects/assets-kamishibai/photos/candidates-inmu/source/famous-face-200.jpg"
)
EYEBAR_DIR = Path(r"C:/Users/shuya/Projects/assets-kamishibai/photos/candidates-inmu")
OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260909-inmu-kamishibai")
SPRITES = Path(r"C:/Users/shuya/Projects/assets-kamishibai/sprites")

CFG = Kamishibai()

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")

W, H = 1280, 720

WHITE = (255, 255, 255, 255)
YELLOW = (247, 226, 122, 255)
BLACK_STROKE = (10, 10, 10, 255)

# 目線バーの座標（元画像 200x200 基準。グリッド画像で目視して決定）。
# 眉の少し上から、目の下・鼻梁の上まで。顔幅よりやや広め。
BAR_LEFT_200 = 12
BAR_RIGHT_200 = 146
BAR_TOP_200 = 58
BAR_BOTTOM_200 = 97
UPSCALE = 4


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


def draw_mixed_center(base: Image.Image, segments: list[tuple[str, tuple]], center_x: int, center_y: int,
                       font: ImageFont.FreeTypeFont, stroke_width: int, stroke_fill=BLACK_STROKE) -> None:
    """segments = [(text, color), ...] を横に並べて中央寄せで描く（1文字列内の部分強調色用）。"""
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


def darken(base: Image.Image, amount: float) -> None:
    veil = Image.new("RGBA", base.size, (0, 0, 0, round(255 * amount)))
    base.alpha_composite(veil)


def load_puppet(character_dir: str, expression: str, target_height: int) -> Image.Image:
    """立ち絵を読み、余白をトリムして目標高にリサイズし、白い縁を付ける（前作 gender-wars 版を踏襲）。"""
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


# ---------------------------------------------------------------------------
# 1. 目線バー画像
# ---------------------------------------------------------------------------

def make_eyebar_images() -> None:
    EYEBAR_DIR.mkdir(parents=True, exist_ok=True)
    src = Image.open(SOURCE_IMG).convert("RGB")

    # 200px版: そのまま黒帯を描く
    img200 = src.copy()
    d200 = ImageDraw.Draw(img200)
    d200.rectangle([BAR_LEFT_200, BAR_TOP_200, BAR_RIGHT_200, BAR_BOTTOM_200], fill=(0, 0, 0))
    img200.save(EYEBAR_DIR / "famous-face-eyebar-200.png")

    # 800px版: 先に4倍拡大(Lanczos)してから黒帯を描く(縁をくっきりさせるため)
    img800 = src.resize((src.width * UPSCALE, src.height * UPSCALE), Image.LANCZOS)
    d800 = ImageDraw.Draw(img800)
    d800.rectangle(
        [BAR_LEFT_200 * UPSCALE, BAR_TOP_200 * UPSCALE, BAR_RIGHT_200 * UPSCALE, BAR_BOTTOM_200 * UPSCALE],
        fill=(0, 0, 0),
    )
    img800.save(EYEBAR_DIR / "famous-face-eyebar-800.png")


# ---------------------------------------------------------------------------
# 2. サムネ3案
# ---------------------------------------------------------------------------

LINE1_SEGMENTS = [("なぜ", WHITE), ("淫夢", YELLOW), ("に", WHITE)]
LINE2_TEXT = "熱狂するのか？"

# A2: めたん・ずんだもんを添える改訂案の文言（2026-09-09 ユーザー指示）。
# 1行目は「淫夢は」「なぜ人気？」の2段、2行目は副題として1段に収める。
LINE2_TEXT_A2 = "ネットミーム×笑いのメカニズム"


def make_thumb_a() -> Image.Image:
    """顔を右側に高さいっぱい、左に文言。背景は濃紺の単色グラデーション。"""
    bg = vertical_gradient(W, H, (18, 20, 30), (34, 30, 46))

    face = Image.open(EYEBAR_DIR / "famous-face-eyebar-800.png").convert("RGBA")
    face = face.resize((H, H), Image.LANCZOS)  # 正方形を高さいっぱいに
    bg.alpha_composite(face, (W - H, 0))

    left_center_x = (W - H) // 2
    f1 = fit_bold_font("なぜ淫夢に", max_width=round((W - H) * 0.86), max_height=round(H * 0.20), stroke_width=9)
    draw_mixed_center(bg, LINE1_SEGMENTS, left_center_x, round(H * 0.40), f1, stroke_width=9)
    f2 = fit_bold_font(LINE2_TEXT, max_width=round((W - H) * 0.86), max_height=round(H * 0.20), stroke_width=9)
    draw_mixed_center(bg, [(LINE2_TEXT, WHITE)], left_center_x, round(H * 0.60), f2, stroke_width=9)
    return bg


def make_thumb_a2() -> Image.Image:
    """A案 + 文言を大幅拡大（1行目は2段の特大文字）、左下にめたん・ずんだもんを大きく
    （高さ76%、下端は画面外）配置する改訂版。

    2026-09-09 二度目のユーザー指示: 「二人が小さすぎる、下半身が画面外にはみ出してよいので
    腰から上を大きく見せる」との指摘を受け、立ち絵の高さを 38%→76% に拡大。その分の余白を
    作るため、文言ブロック（2段の見出し＋副題）は上45%に収め、1段目フォントを幅最大値から
    12%縮める。
    """
    bg = vertical_gradient(W, H, (18, 20, 30), (34, 30, 46))

    face = Image.open(EYEBAR_DIR / "famous-face-eyebar-800.png").convert("RGBA")
    face = face.resize((H, H), Image.LANCZOS)
    bg.alpha_composite(face, (W - H, 0))

    left_w = W - H  # 560（顔の左端まで）
    left_center_x = left_w // 2
    draw = ImageDraw.Draw(bg)
    stroke_big = 11

    # 1行目: 「淫夢は」「なぜ人気？」を2段。まず幅いっぱいに最大化し、そこから12%縮めて
    # 文言ブロックを上45%以内に収める。
    text_max_w = round(left_w * 0.95)
    f1a_full = fit_bold_font("淫夢は", max_width=text_max_w, max_height=round(H * 0.42), stroke_width=stroke_big)
    f1b_full = fit_bold_font("なぜ人気？", max_width=text_max_w, max_height=round(H * 0.42), stroke_width=stroke_big)
    shrink = 0.84
    f1a = _font(round(f1a_full.size * shrink))
    f1b = _font(round(f1b_full.size * shrink))
    bbox_1a = draw.textbbox((0, 0), "淫夢は", font=f1a, stroke_width=stroke_big)
    h_1a = bbox_1a[3] - bbox_1a[1]
    bbox_1b = draw.textbbox((0, 0), "なぜ人気？", font=f1b, stroke_width=stroke_big)
    h_1b = bbox_1b[3] - bbox_1b[1]

    line_gap = round(H * 0.008)
    top_y = round(H * 0.01)
    y1a = top_y + h_1a / 2
    y1b = top_y + h_1a + line_gap + h_1b / 2
    draw_mixed_center(bg, [("淫夢", YELLOW), ("は", WHITE)], left_center_x, round(y1a), f1a, stroke_width=stroke_big)
    draw_mixed_center(bg, [("なぜ人気？", WHITE)], left_center_x, round(y1b), f1b, stroke_width=stroke_big)
    text_block_bottom = y1b + h_1b / 2

    # 2行目（副題）: 半透明の黒帯を敷いてから、幅いっぱいの最大サイズで重ねる。
    stroke_sub = 6
    f2 = fit_bold_font(LINE2_TEXT_A2, max_width=round(left_w * 0.97), max_height=round(H * 0.07), stroke_width=stroke_sub)
    bbox_2 = draw.textbbox((0, 0), LINE2_TEXT_A2, font=f2, stroke_width=stroke_sub)
    h_2 = bbox_2[3] - bbox_2[1]
    band_pad = round(H * 0.008)
    band_top = round(text_block_bottom + H * 0.008)
    band_bottom = band_top + h_2 + band_pad * 2
    band = Image.new("RGBA", (left_w, band_bottom - band_top), (0, 0, 0, round(255 * 0.60)))
    bg.alpha_composite(band, (0, band_top))
    y2 = (band_top + band_bottom) / 2
    draw_mixed_center(bg, [(LINE2_TEXT_A2, WHITE)], left_center_x, round(y2), f2, stroke_width=stroke_sub)

    # 立ち絵: 高さ76%（下端は画面外にはみ出させ、腰から上を大きく見せる）。
    # 頭頂は画面高さ47%あたり（文言ブロックの下、45〜50%の指示範囲）。ずんだもんを手前に
    # （後から貼るレイヤーが手前になる）、左下で少し重ねる。
    puppet_h = round(H * 0.76)
    metan = load_puppet("metan", "smile", puppet_h)
    zun = load_puppet("zundamon", "normal", puppet_h)
    head_top_y = round(H * 0.47)
    metan_cx = round(left_w * 0.30)
    zun_cx = round(left_w * 0.64)
    paste(bg, metan, metan_cx - metan.width / 2, head_top_y)
    paste(bg, zun, zun_cx - zun.width / 2, head_top_y)
    return bg


def make_thumb_b() -> Image.Image:
    """顔を中央いっぱいに、文言を上下に分けて重ねる。顔は少し暗くする。"""
    face = Image.open(EYEBAR_DIR / "famous-face-eyebar-800.png").convert("RGBA")
    bg = cover_fit(face, W, H)
    darken(bg, 0.42)

    f1 = fit_bold_font("なぜ淫夢に", max_width=round(W * 0.90), max_height=round(H * 0.20), stroke_width=10)
    draw_mixed_center(bg, LINE1_SEGMENTS, W // 2, round(H * 0.20), f1, stroke_width=10)
    f2 = fit_bold_font(LINE2_TEXT, max_width=round(W * 0.90), max_height=round(H * 0.20), stroke_width=10)
    draw_mixed_center(bg, [(LINE2_TEXT, WHITE)], W // 2, round(H * 0.80), f2, stroke_width=10)
    return bg


def _draw_comment_lines(bg: Image.Image, x0: int, x1: int) -> None:
    import random

    rng = random.Random(32)
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for y in range(30, H - 30, 26):
        seg_w = rng.randint(round((x1 - x0) * 0.3), round((x1 - x0) * 0.85))
        sx = rng.randint(x0, max(x0, x1 - seg_w))
        alpha = rng.randint(50, 110)
        d.line([(sx, y), (sx + seg_w, y)], fill=(255, 255, 255, alpha), width=3)
    bg.alpha_composite(overlay)


def make_thumb_c() -> Image.Image:
    """顔を左に小さめ(高さ60%)、右にニコニコ風の白い横線群、文言は右下。"""
    bg = Image.new("RGBA", (W, H), (12, 12, 16, 255))

    face_h = round(H * 0.60)
    face = Image.open(EYEBAR_DIR / "famous-face-eyebar-800.png").convert("RGBA")
    face = face.resize((face_h, face_h), Image.LANCZOS)
    face_x = round(W * 0.06)
    face_y = (H - face_h) // 2
    bg.alpha_composite(face, (face_x, face_y))

    lines_x0 = face_x + face_h + round(W * 0.03)
    _draw_comment_lines(bg, lines_x0, W - round(W * 0.03))

    right_center_x = lines_x0 + (W - round(W * 0.03) - lines_x0) // 2
    f1 = fit_bold_font("なぜ淫夢に", max_width=round((W - lines_x0) * 0.92), max_height=round(H * 0.16), stroke_width=8)
    draw_mixed_center(bg, LINE1_SEGMENTS, right_center_x, round(H * 0.72), f1, stroke_width=8)
    f2 = fit_bold_font(LINE2_TEXT, max_width=round((W - lines_x0) * 0.92), max_height=round(H * 0.16), stroke_width=8)
    draw_mixed_center(bg, [(LINE2_TEXT, WHITE)], right_center_x, round(H * 0.88), f2, stroke_width=8)
    return bg


# ---------------------------------------------------------------------------
# 3. コンタクトシート
# ---------------------------------------------------------------------------

def make_contact_sheet(images: list[Image.Image], labels: list[str]) -> Image.Image:
    n = len(images)
    scale_w = W // n
    scale_h = round(H * scale_w / W)
    sheet = Image.new("RGB", (scale_w * n, scale_h), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    label_font = _font(round(scale_h * 0.10))
    for i, (img, label) in enumerate(zip(images, labels)):
        tile = img.convert("RGB").resize((scale_w, scale_h), Image.LANCZOS)
        sheet.paste(tile, (i * scale_w, 0))
        lx, ly = i * scale_w + 10, 8
        draw.text((lx, ly), label, font=label_font, fill=(255, 255, 255),
                  stroke_width=4, stroke_fill=(0, 0, 0))
    return sheet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_eyebar_images()

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

    # A2: 文言拡大版で上書き（A3・A4は廃止、2026-09-09）。
    img_a2 = make_thumb_a2()
    p = OUT / "thumb-A2.png"
    img_a2.convert("RGB").save(p, "PNG", optimize=True)
    print(p)

    small_w = 480
    small_h = round(H * small_w / W)
    p_small = OUT / "thumb-A2-small.jpg"
    img_a2.convert("RGB").resize((small_w, small_h), Image.LANCZOS).save(p_small, quality=90)
    print(p_small)


if __name__ == "__main__":
    main()
