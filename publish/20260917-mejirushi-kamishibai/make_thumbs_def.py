# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（「めじるしアクセサリーはなぜ流行ったのか」・紙芝居版, Issue #40）。

背景は白い 3D の棒人間（顔のない、つるっとした白いヒューマノイド）を使った 3 案（A/B/C）。
comparison-kamishibai の `make_thumbs_def.py`（place_top_aligned 方式）を踏襲する。

- A: 10 体が横一列に並び、同じ小さな丸いチャームをバッグにぶら下げている。1 体だけ違う色。
- B: ガチャガチャの機械の前に行列が伸び、先頭の 1 体が回している。
- C: 傘立てに同じ透明の傘が並び、1 体だけ自分の傘を探して首をかしげている。

背景は横幅いっぱい（等比・幅合わせ）に置き、縮小はせず、画像を下へずらして
「一番上の人物の頂点」を上帯の下端に合わせる（place_top_aligned。2026-09-16 の
comparison-kamishibai での決定を踏襲）。「？」の重ね書きはしない（絵自体で意味が
伝わるため。2026-09-17 ユーザー指示）。
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

OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260917-mejirushi-kamishibai")
SPRITES = Path(r"C:/Users/shuya/Projects/assets-kamishibai/sprites")
BG_DIR = OUT / "thumb-bg"

CFG = Kamishibai()

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")

W, H = 1280, 720

WHITE = (255, 255, 255, 255)
GOLD = (194, 169, 112, 255)  # design-chic-tone.md の金アクセント #C2A970
BLACK_STROKE = (10, 10, 10, 255)

TITLE_TOP = "なぜ流行ったのか"

# (背景ファイル, 下帯の文言, 出力ファイル名, めたんの表情, ずんだもんの表情)
VARIANTS = [
    ("bg-A.png", "6年前からあった", "thumb-A.png", "explain", "surprised"),
    ("bg-B.png", "商品は同じだった", "thumb-B.png", "serious", "confused"),
    ("bg-C.png", "みんな同じで、私だけ違う", "thumb-C.png", "smile", "thinking"),
]

# 上帯（タイトル文言を置く領域）の下端。背景の「一番上の人物」の頂点を
# ここに合わせる（縮小せず下へずらす）。
TOP_SAFE = round(H * 0.21)

# 各背景の「一番上の白い人物」の頂点行（元画像座標。輝度 >238 の画素が 4 個以上ある
# 最初の行を計測した値）。
FIGURE_TOP = {
    "bg-A.png": 96,
    "bg-B.png": 28,
    "bg-C.png": 30,
}

# 背景の水平ずらし（px、正で右へ）。幅合わせ配置ではずらすと端に地色の帯が出るため 0。
H_BIAS = {
    "bg-A.png": 0,
    "bg-B.png": 0,
    "bg-C.png": 0,
}


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


def sample_fill_color(photo: Image.Image) -> tuple[int, int, int, int]:
    """背景の地色（薄いグレー）を、人物が写り込みにくい左右上端の隅から採取する。"""
    img = photo.convert("RGB")
    w, h = img.size
    patch = 60
    pixels = list(img.crop((0, 0, patch, patch)).getdata())
    pixels += list(img.crop((w - patch, 0, w, patch)).getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return (r, g, b, 255)


def place_top_aligned(canvas: Image.Image, photo: Image.Image, figure_top_src: int, top_y: int,
                      hbias: int = 0) -> tuple[float, int, int]:
    """photo を等比でキャンバス幅いっぱいに合わせ（縮小はしない）、元画像の
    `figure_top_src` 行がキャンバスの `top_y` に来るよう下へずらして貼る。はみ出した
    下端はキャンバス外。戻り値 (scale, x0, y0) は元画像座標→キャンバス座標の係数
    （final = (src_x*scale+x0, src_y*scale+y0)）。"""
    img = photo.convert("RGBA")
    w, h = img.size
    scale = canvas.width / w
    new_w, new_h = canvas.width, round(h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    x0 = hbias
    y0 = top_y - round(figure_top_src * scale)
    canvas.paste(resized, (x0, y0), resized)
    return scale, x0, y0


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
    fill = sample_fill_color(photo)
    bg = Image.new("RGBA", (W, H), fill)
    hbias = H_BIAS.get(bg_path.name, 0)
    place_top_aligned(bg, photo, FIGURE_TOP[bg_path.name], TOP_SAFE, hbias=hbias)

    # 立ち絵: 「下端から顔が覗く」配置。文言より先に貼り、下帯の文言を
    # 立ち絵の上に重ねて描くことで、文字が立ち絵に隠れないようにする。
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

    # 下段（最下部の全幅帯）: 金文字・案ごとの副題。立ち絵の上に重ねて描く。
    f2 = fit_bold_font(subtitle, max_width=round(W * 0.86), max_height=round(H * 0.14), stroke_width=9)
    draw_mixed_center(bg, [(subtitle, GOLD)], W // 2, round(H * 0.90), f2, stroke_width=9)

    return bg


def make_contact_sheet(images: list[Image.Image], labels: list[str]) -> Image.Image:
    n = len(images)
    scale_w = 320
    scale_h = round(H * scale_w / W)
    sheet = Image.new("RGB", (scale_w * n, scale_h), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_BOLD), round(scale_h * 0.14))
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
    p = OUT / "thumb-contact-ABC.jpg"
    sheet.save(p, quality=88)
    print(p)


if __name__ == "__main__":
    main()
