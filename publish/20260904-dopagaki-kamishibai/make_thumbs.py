# -*- coding: utf-8 -*-
"""サムネイル合成スクリプト（ドパガキ・紙芝居版）。

script-to-video の紙芝居舞台描画（`kamishibai.py`）の部品（黒板下地・立ち絵の紙縁・貼り
写真の紙縁演出）を流用し、1280x720 のサムネイル3案を Pillow で合成する。

黒板の舞台は `compute_stage(1280, 900, Kamishibai())` で作る（caption_band_ratio 既定 0.20
により caption_band_top がちょうど 720 になる高さを逆算）。字幕帯を含まない
`0..caption_band_top` の範囲がそのまま 1280x720 になるため、拡縮・トリミングなしで
木枠が四辺に見える下地が得られる（本編のような歪みが出ない）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\shuya\Projects\script-to-video\src")

from PIL import Image, ImageDraw, ImageFont

from script_to_video.kamishibai import (
    add_paper_outline,
    chalk_text_layer,
    compute_stage,
    load_sprite,
    render_board_plate,
    _chalk_font,
    _compose_pasted_photo,
)
from script_to_video.schema import Kamishibai

OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260904-dopagaki-kamishibai")
SPRITES = Path(r"C:/Users/shuya/Projects/assets-kamishibai/sprites")
PHOTO_PATH = Path(r"C:/Users/shuya/Projects/assets-kamishibai/render-assets/scene_01_beat1.jpg")

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")

W, H = 1280, 720

WHITE = (255, 255, 255, 255)
YELLOW = (247, 226, 122, 255)  # #F7E27A
BLACK_STROKE = (10, 10, 10, 255)

CFG = Kamishibai()


def build_stage_and_bg():
    """紙芝居の黒板下地（1280x720、字幕帯なし）と `Stage` を作る。"""

    stage = compute_stage(W, 900, CFG)
    assert stage.caption_band_top == H, stage.caption_band_top
    plate = render_board_plate(stage, CFG)
    bg = plate.crop((0, 0, W, H)).convert("RGBA")
    return stage, bg


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
    クリップされる（下端を切って半身だけ見せる C 案などに使う）。"""

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


def paste_chalk_center(base: Image.Image, text: str, center_x: int, top_y: int, size: int,
                        color: tuple[int, int, int] = (238, 236, 226)) -> Image.Image:
    """チョーク文字1行を中央揃えで貼る（副題用）。貼ったレイヤーを返す。"""

    layer = chalk_text_layer(text, _chalk_font(size), color=color)
    x = round(center_x - layer.width / 2)
    paste(base, layer, x, top_y)
    return layer


def save(img: Image.Image, name: str) -> Path:
    out = img.convert("RGB")
    path = OUT / name
    out.save(path, "PNG", optimize=True)
    return path


# ============================================================
# A: 人形＋大文字
# ============================================================

def make_thumb_a() -> Image.Image:
    stage, bg = build_stage_and_bg()
    bl, bt, br, bb = stage.board_rect
    board_w = br - bl

    metan_h = round(H * 0.83)
    zun_h = round(H * 0.78)
    metan = load_puppet("metan", "explain", metan_h)
    zun = load_puppet("zundamon", "confused", zun_h)

    foot_y = bb + round(H * 0.010)  # 木枠の受け皿あたりまで足を下ろす
    metan_cx = bl + round(board_w * 0.235)
    zun_cx = br - round(board_w * 0.235)

    paste(bg, metan, metan_cx - metan.width / 2, foot_y - metan.height)
    paste(bg, zun, zun_cx - zun.width / 2, foot_y - zun.height)

    # 中央の大文字（人形の手前）。
    center_x = (bl + br) // 2
    sub_top_font = _chalk_font(round(H * 0.062))
    paste_chalk_center(bg, "なぜ現代人は", center_x, round(H * 0.075), round(H * 0.062))

    big_font = fit_bold_font("ドパガキ", max_width=round(board_w * 0.62), max_height=round(H * 0.46), stroke_width=10)
    draw_bold_center(bg, "ドパガキ", center_x, round(H * 0.47), big_font, YELLOW, stroke_width=10)

    paste_chalk_center(bg, "になってしまうのか？", center_x, round(H * 0.775), round(H * 0.062))

    return bg


# ============================================================
# B: 写真＋一言
# ============================================================

def make_thumb_b() -> Image.Image:
    stage, bg = build_stage_and_bg()
    bl, bt, br, bb = stage.board_rect
    board_w = br - bl

    photo = Image.open(PHOTO_PATH).convert("RGB")
    photo_layer = _compose_pasted_photo(photo, stage, round(board_w * 0.86))
    px = (bl + br) // 2 - photo_layer.width // 2
    py = bt - round(H * 0.02)
    paste(bg, photo_layer, px, py)

    metan_h = round(H * 0.55)
    zun_h = round(H * 0.52)
    metan = load_puppet("metan", "serious", metan_h)
    zun = load_puppet("zundamon", "sleepy", zun_h)
    foot_y = bb + round(H * 0.010)
    metan_cx = bl + round(board_w * 0.09)
    zun_cx = br - round(board_w * 0.09)
    paste(bg, metan, metan_cx - metan.width / 2, foot_y - metan.height)
    paste(bg, zun, zun_cx - zun.width / 2, foot_y - zun.height)

    center_x = (bl + br) // 2
    line1_font = fit_bold_font("ドーパミン中毒は", max_width=round(board_w * 0.80), max_height=round(H * 0.115), stroke_width=7)
    draw_bold_center(bg, "ドーパミン中毒は", center_x, round(H * 0.125), line1_font, WHITE, stroke_width=7)

    # 下端の安全マージン(40px)を必ず割り込まないよう、visual_bottom = center_y + h/2 で逆算する。
    line2_font = fit_bold_font("半分ウソ", max_width=round(board_w * 0.70), max_height=round(H * 0.24), stroke_width=11)
    draw_bold_center(bg, "半分ウソ", center_x, round(H * 0.80), line2_font, YELLOW, stroke_width=11)

    return bg


# ============================================================
# C: 対比の板書
# ============================================================

def make_thumb_c() -> Image.Image:
    stage, bg = build_stage_and_bg()
    bl, bt, br, bb = stage.board_rect
    board_w = br - bl
    center_x = (bl + br) // 2

    line1_font = fit_bold_font("弱くなったのは脳？", max_width=round(board_w * 0.90), max_height=round(H * 0.185), stroke_width=8)
    draw_bold_center(bg, "弱くなったのは脳？", center_x, round(H * 0.30), line1_font, WHITE, stroke_width=8)

    line2_font = fit_bold_font("強くなったのは画面。", max_width=round(board_w * 0.90), max_height=round(H * 0.20), stroke_width=10)
    draw_bold_center(bg, "強くなったのは画面。", center_x, round(H * 0.545), line2_font, YELLOW, stroke_width=10)

    # 人形は下端で半身だけ見せる（顔と肩まで。画面下端でクリップ）。
    metan_h = round(H * 1.30)
    zun_h = round(H * 1.30)
    metan = load_puppet("metan", "serious", metan_h)
    zun = load_puppet("zundamon", "surprised", zun_h)

    visible_h = round(H * 0.40)  # 画面下端から見せたい高さ（顔＋肩まで）
    metan_cx = bl + round(board_w * 0.22)
    zun_cx = br - round(board_w * 0.22)
    metan_top = H - visible_h
    zun_top = H - visible_h

    paste(bg, metan, metan_cx - metan.width / 2, metan_top)
    paste(bg, zun, zun_cx - zun.width / 2, zun_top)

    return bg


if __name__ == "__main__":
    a = make_thumb_a()
    b = make_thumb_b()
    c = make_thumb_c()

    for img, name in ((a, "thumb-A.png"), (b, "thumb-B.png"), (c, "thumb-C.png")):
        path = save(img, name)
        size_kb = path.stat().st_size / 1024
        print(f"{path}: {img.size} mode={img.mode} -> {size_kb:.1f} KB")
