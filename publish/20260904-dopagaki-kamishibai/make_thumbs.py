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


# ============================================================
# D/E/F: 写真全面＋大見出し（ユーザーFB反映。黒板を使わない案）
# ============================================================

PHOTOS_DIR = Path(r"C:/Users/shuya/Projects/assets-kamishibai/photos/candidates-v4")
PHOTO_D = PHOTOS_DIR / "bed" / "bed-woman-lamp-nightside.jpg"
PHOTO_E = PHOTOS_DIR / "thumb" / "thumb-photogrid-laptop-bright.jpg"

HEADLINE_SMALL_RATIO = 0.55
"""1行目の「なぜ」「に」の文字サイズ＝「ドパガキ」の何割か（下揃え）。"""

HEADLINE_MAX_WIDTH = W - 80
"""見出しの横幅上限（左右マージン40pxずつ）。"""

HEADLINE_MAX_TOTAL_HEIGHT = round(H * 0.52)
"""2行合計の高さ上限（画面高の45〜55%レンジのねらい値）。"""


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


def fit_and_draw_headline(base: Image.Image, center_x: int, block_center_y: int, *,
                           max_width: int = HEADLINE_MAX_WIDTH,
                           max_total_height: int = HEADLINE_MAX_TOTAL_HEIGHT,
                           stroke_width: int = 10, small_ratio: float = HEADLINE_SMALL_RATIO,
                           max_size: int = 400) -> dict:
    """2行見出し「なぜドパガキに」／「になってしまうのか？」を描く。

    「ドパガキ」だけ大きく黄色（`YELLOW`）、他は白。1行目の「なぜ」「に」は「ドパガキ」より
    小さく、下揃えで並べる。幅・高さの両方の上限に収まる最大サイズを二分探索で決める。
    実際に使ったサイズ等を dict で返す（報告用）。
    """

    prefix, big_word, suffix = "なぜ", "ドパガキ", "に"
    line2_text = "なってしまうのか？"

    tmp = Image.new("RGBA", (10, 10))
    probe = ImageDraw.Draw(tmp)
    line_gap = round(max_total_height * 0.06)

    def metrics(large_size: int):
        small_size = max(8, round(large_size * small_ratio))
        large_font = _font(large_size)
        small_font = _font(small_size)
        b_prefix = probe.textbbox((0, 0), prefix, font=small_font, stroke_width=stroke_width)
        b_big = probe.textbbox((0, 0), big_word, font=large_font, stroke_width=stroke_width)
        b_suffix = probe.textbbox((0, 0), suffix, font=small_font, stroke_width=stroke_width)
        b_line2 = probe.textbbox((0, 0), line2_text, font=small_font, stroke_width=stroke_width)
        line1_w = (b_prefix[2] - b_prefix[0]) + (b_big[2] - b_big[0]) + (b_suffix[2] - b_suffix[0])
        line1_h = b_big[3] - b_big[1]
        line2_w = b_line2[2] - b_line2[0]
        line2_h = b_line2[3] - b_line2[1]
        return large_font, small_font, b_prefix, b_big, b_suffix, b_line2, line1_w, line1_h, line2_w, line2_h

    lo, hi = 10, max_size
    best_size = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        *_, line1_w, line1_h, line2_w, line2_h = metrics(mid)
        if line1_w <= max_width and line2_w <= max_width and (line1_h + line_gap + line2_h) <= max_total_height:
            best_size = mid
            lo = mid + 1
        else:
            hi = mid - 1

    large_font, small_font, b_prefix, b_big, b_suffix, b_line2, line1_w, line1_h, line2_w, line2_h = metrics(best_size)
    total_h = line1_h + line_gap + line2_h
    block_top = block_center_y - total_h / 2
    line1_bottom = block_top + line1_h
    line2_bottom = line1_bottom + line_gap + line2_h

    draw = ImageDraw.Draw(base)

    # 1行目: 「なぜ」(小・白) + 「ドパガキ」(大・黄) + 「に」(小・白)。下揃え。
    cursor = center_x - line1_w / 2
    for text, font, bbox, fill in (
        (prefix, small_font, b_prefix, WHITE),
        (big_word, large_font, b_big, YELLOW),
        (suffix, small_font, b_suffix, WHITE),
    ):
        w = bbox[2] - bbox[0]
        x = cursor - bbox[0]
        y = line1_bottom - bbox[3]
        draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=BLACK_STROKE)
        cursor += w

    # 2行目: 全体白、中央揃え、1行目と同じ小サイズ。
    x2 = center_x - line2_w / 2 - b_line2[0]
    y2 = line2_bottom - b_line2[3]
    draw.text((x2, y2), line2_text, font=small_font, fill=WHITE, stroke_width=stroke_width, stroke_fill=BLACK_STROKE)

    return {
        "large_size_px": large_font.size,
        "small_size_px": small_font.size,
        "total_height_px": round(total_h),
        "total_height_ratio": round(total_h / H, 3),
        "line1_bottom": round(line1_bottom),
        "line2_bottom": round(line2_bottom),
    }


def place_corner_puppets(base: Image.Image, left_dir: str, left_expr: str, right_dir: str, right_expr: str,
                          target_height: int, edge_margin: int = 10) -> None:
    """人形を画面下の左右角に置く（写真の上、見出しテキストの後ろ＝先に呼ぶこと）。"""

    left = load_puppet(left_dir, left_expr, target_height)
    right = load_puppet(right_dir, right_expr, target_height)
    paste(base, left, edge_margin, H - left.height)
    paste(base, right, W - edge_margin - right.width, H - right.height)


def make_thumb_d() -> tuple[Image.Image, dict]:
    """D: ベッドでスマホ（夜ふかし）＋人形（めたん thinking／ずんだもん sleepy）。"""

    bg = cover_fit(Image.open(PHOTO_D), W, H)
    darken(bg, 0.30)
    place_corner_puppets(bg, "metan", "thinking", "zundamon", "sleepy", round(H * 0.42))
    info = fit_and_draw_headline(bg, W // 2, round(H * 0.47))
    return bg, info


def make_thumb_e() -> tuple[Image.Image, dict]:
    """E: 明るいフィードを親指操作（ショート動画）＋人形（めたん point／ずんだもん confused）。
    写真が明るいので暗幕をやや強めにする。"""

    bg = cover_fit(Image.open(PHOTO_E), W, H)
    darken(bg, 0.42)
    place_corner_puppets(bg, "metan", "point", "zundamon", "confused", round(H * 0.42))
    info = fit_and_draw_headline(bg, W // 2, round(H * 0.47))
    return bg, info


def make_thumb_f() -> tuple[Image.Image, dict]:
    """F: D と同じ写真・暗幕で人形なし（比較用）。"""

    bg = cover_fit(Image.open(PHOTO_D), W, H)
    darken(bg, 0.30)
    info = fit_and_draw_headline(bg, W // 2, round(H * 0.47))
    return bg, info


if __name__ == "__main__":
    a = make_thumb_a()
    b = make_thumb_b()
    c = make_thumb_c()
    d, info_d = make_thumb_d()
    e, info_e = make_thumb_e()
    f, info_f = make_thumb_f()

    for img, name in ((a, "thumb-A.png"), (b, "thumb-B.png"), (c, "thumb-C.png"),
                       (d, "thumb-D.png"), (e, "thumb-E.png"), (f, "thumb-F.png")):
        path = save(img, name)
        size_kb = path.stat().st_size / 1024
        print(f"{path}: {img.size} mode={img.mode} -> {size_kb:.1f} KB")

    for name, info in (("D", info_d), ("E", info_e), ("F", info_f)):
        print(f"{name} headline: {info}")
