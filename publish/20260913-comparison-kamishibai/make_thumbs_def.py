# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト・第2弾（「人はなぜ他人と比べてしまうのか」・紙芝居版, Issue #38）。

A/B/C（`make_thumbs.py`、実写風の夜のスマホ場面）とは別構図の D/E/F 案。
背景は白い 3D の棒人間（顔のない、つるっとした白いヒューマノイド）が表彰台に立つ場面
（Codex 生成、`thumb-bg/orig/bg-{D,E,F}-raw.png`）。1位・3位は喜んでいるが2位だけ
うなだれている構図で「比べる」の意味を絵で伝える。A/B/C で使った金色の大きな「？」の
重ね書きは今回は使わない（絵自体で意味が伝わるため）。D 案だけ、2位の頭上に小さい
「？」を置いた `thumb-D2.png` も追加で作る。

合成の骨格（上下2帯・立ち絵の配置）は `make_thumbs.py` を踏襲するが、背景の配置方法は
異なる。表彰台3人＋4人目が全員はっきり見える必要があるため、背景は**横幅いっぱい
（等比・幅合わせ）に置き、縮小はせず、画像を下へずらして「1位の拳の頂点」を上帯の
下端に合わせる**。下帯の文言とは重なってよい（2026-09-16 ユーザー指示。それ以前の
「上下帯の間に等比縮小で収める」contain-fit は、人物が小さくなりすぎるため取りやめ）。
下端は 60〜70px ほどキャンバス外に出る（床の反射と 4 人目の足先）。
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
    ("bg-D.png", "2位はなぜ落ち込むのか", "thumb-D.png", "thinking", "confused"),
    ("bg-E.png", "比べるのはやめられない", "thumb-E.png", "serious", "sad"),
    ("bg-F.png", "SNSで病む理由", "thumb-F.png", "explain", "thinking"),  # 採用案（ユーザー選択 2026-09-16。旧文言「順位より、何と比べたか」）
]

# 上帯（タイトル文言を置く領域）の下端。背景の「一番上の人物（1位の拳）」の頂点を
# ここに合わせる（縮小せず下へずらす）。
TOP_SAFE = round(H * 0.21)

# 各背景の「一番上の白い人物」の頂点行（元画像座標。輝度 >238 の画素が 4 個以上ある
# 最初の行を計測した値）。
FIGURE_TOP = {
    "bg-D.png": 31,
    "bg-E.png": 17,
    "bg-F.png": 41,
}

# 上段タイトル文字の下端（実測値。fit_bold_font(TITLE_TOP, W*0.92, H*0.16, stroke=8) で
# 描画したときのテキスト bbox 下端が canvas y=124 になる。D2 の「？」をタイトルへ
# めり込ませずに置くための計算に使う）。
TITLE_BOTTOM_PX = 124

# D2: D と同じ背景・文言に、2位の頭上へ大きめの金色「？」を1つ追加する。
# 幅合わせ配置では 2位の頭上端（元画像 y≈220）がキャンバス y≈296 に来るので、
# タイトル下端（124）との間に約170px の隙間があり、0.18H（130px）の「？」が収まる。
D2_MARK_H = round(H * 0.18)
D2_MARK_CX_SRC_FRAC = 0.556  # 2位の頭の中心 x（bg-D.png 内の比率。目視で計測）
D2_HEAD_TOP_SRC = 220        # 2位の頭の上端 y（bg-D.png 内の px。目視で計測）

# 背景の水平ずらし（px、正で右へ）。幅合わせ配置ではずらすと端に地色の帯が出るため 0。
H_BIAS = {
    "bg-D.png": 0,
    "bg-E.png": 0,
    "bg-F.png": 0,
}
# 立ち絵を小さくした版（-s）の水平ずらし。端に出る地色の帯（40px）は壁と同じグレーで
# ほぼ見えず、大半は立ち絵の後ろに隠れる。
H_BIAS_SMALL = {
    "bg-D.png": -40,  # 4人目が右端 → 左へ
    "bg-E.png": 40,   # 4人目が左端 → 右へ
    "bg-F.png": 0,
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


def make_thumb(bg_path: Path, subtitle: str, metan_expr: str, zun_expr: str,
                small_mark: bool = False, small_puppets: bool = False) -> Image.Image:
    """small_puppets=True: 立ち絵を 0.65H→0.45H に縮めて両隅へ寄せ（cx 0.08 / 0.92）、
    背景を H_BIAS_SMALL だけ横にずらして 4 人目（体育座り）が立ち絵の後ろに隠れない
    ようにする（D/E 用。F は 4 人目がいないので不要）。"""
    photo = Image.open(bg_path)
    fill = sample_fill_color(photo)
    bg = Image.new("RGBA", (W, H), fill)
    hbias = (H_BIAS_SMALL if small_puppets else H_BIAS).get(bg_path.name, 0)
    scale, x0, y0 = place_top_aligned(bg, photo, FIGURE_TOP[bg_path.name], TOP_SAFE, hbias=hbias)

    if small_mark:
        mark_font = fit_bold_font("？", max_width=D2_MARK_H, max_height=D2_MARK_H, stroke_width=14)
        cx = round(D2_MARK_CX_SRC_FRAC * photo.width * scale + x0)
        head_top = round(D2_HEAD_TOP_SRC * scale + y0)
        cy = round((TITLE_BOTTOM_PX + head_top) / 2)  # タイトル下端と2位の頭上端の中間
        draw_mixed_center(bg, [("？", GOLD)], cx, cy, mark_font, stroke_width=14)

    # 立ち絵: 「下端から顔が覗く」配置。文言より先に貼り、下帯の文言を
    # 立ち絵の上に重ねて描くことで、文字が立ち絵に隠れないようにする。
    puppet_h = round(H * (0.45 if small_puppets else 0.65))
    metan = load_puppet("metan", metan_expr, puppet_h)
    zun = load_puppet("zundamon", zun_expr, puppet_h)
    peek_top_y = H - round(puppet_h * 0.5)
    metan_cx = round(W * (0.08 if small_puppets else 0.12))
    zun_cx = round(W * (0.92 if small_puppets else 0.88))
    paste(bg, metan, metan_cx - metan.width / 2, peek_top_y)
    paste(bg, zun, zun_cx - zun.width / 2, peek_top_y)

    # 上段（最上部の全幅帯）: 白文字・共通の問い
    f1 = fit_bold_font(TITLE_TOP, max_width=round(W * 0.92), max_height=round(H * 0.16), stroke_width=8)
    draw_mixed_center(bg, [(TITLE_TOP, WHITE)], W // 2, round(H * 0.10), f1, stroke_width=8)

    # 下段（最下部の全幅帯）: 金文字・案ごとの副題。立ち絵の上に重ねて描く。
    f2 = fit_bold_font(subtitle, max_width=round(W * 0.66), max_height=round(H * 0.14), stroke_width=9)
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
    p = OUT / "thumb-contact-DEF.jpg"
    sheet.save(p, quality=88)
    print(p)

    # D2: D と同条件に、2位の頭上へ小さい「？」を追加。
    d2 = make_thumb(BG_DIR / "bg-D.png", "2位はなぜ落ち込むのか", "thinking", "confused", small_mark=True)
    p = OUT / "thumb-D2.png"
    d2.convert("RGB").save(p, "PNG", optimize=True)
    print(p)

    # -s 版: 立ち絵を小さくして 4 人目を見せる（D / D2 / E）。
    small = []
    for bg_name, subtitle, out_name, metan_expr, zun_expr in VARIANTS[:2]:
        img = make_thumb(BG_DIR / bg_name, subtitle, metan_expr, zun_expr, small_puppets=True)
        p = OUT / out_name.replace(".png", "-s.png")
        img.convert("RGB").save(p, "PNG", optimize=True)
        print(p)
        small.append((img, out_name.replace("thumb-", "").replace(".png", "-s")))
    d2s = make_thumb(BG_DIR / "bg-D.png", "2位はなぜ落ち込むのか", "thinking", "confused",
                     small_mark=True, small_puppets=True)
    p = OUT / "thumb-D2-s.png"
    d2s.convert("RGB").save(p, "PNG", optimize=True)
    print(p)
    small.insert(1, (d2s, "D2-s"))
    sheet = make_contact_sheet([i for i, _ in small], [l for _, l in small])
    p = OUT / "thumb-contact-DEs.jpg"
    sheet.save(p, quality=88)
    print(p)


if __name__ == "__main__":
    main()
