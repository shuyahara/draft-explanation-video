# -*- coding: utf-8 -*-
"""ショート用サムネイル（short1-thumb.png / short2-thumb.png、1080x1920）を合成する使い捨てスクリプト。
2026-08-28。

ベースは本編サムネのベース画像（横1672x941）を縦1080x1920へトリミングする。9:16の最大幅は
元画像の縦941pxからの逆算で529pxしか取れない（941*9/16≈529）。
- short1: base-A.png（電車内でスマホを見る手元・後ろ姿）。主題は手元のスマホ画面なので、
  頭部より「後ろ姿の肩＋スマホの発光画面」を優先してクロップする。
- short2: base-C.png（古代の柱と、夜のスマホを見る現代のシルエット）。柱が画面中央付近に
  あるため中央クロップをそのまま使う。
文字は net-gender-wars-short 系の規約を踏襲: Meiryo Bold、白＋ゴールド(#C2A970)、
黒縁取り(stroke_width=10)。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(r"C:/Users/shuya/Projects/script-to-video/build/cynicism-thumb")
OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260827-cynicism")

FONT_BOLD = Path(r"C:/Windows/Fonts/meiryob.ttc")
W, H = 1080, 1920

GOLD = (194, 169, 112, 255)
WHITE = (255, 255, 255, 255)


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD), size)


def load_cropped_base(name: str, crop_x0: int | None = None) -> Image.Image:
    img = Image.open(ASSETS / name).convert("RGB")
    w, h = img.size
    target_ratio = W / H
    cw = round(h * target_ratio)
    if crop_x0 is None:
        cx = w // 2
        x0 = cx - cw // 2
    else:
        x0 = crop_x0
    crop = img.crop((x0, 0, x0 + cw, h))
    crop = crop.resize((W, H), Image.LANCZOS)
    return crop.convert("RGBA")


def fit_font_for_lines(lines: list[str], max_width: int, max_size: int = 260) -> ImageFont.FreeTypeFont:
    lo, hi = 10, max_size
    best = _font(lo)
    tmp = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(tmp)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = _font(mid)
        widths = [draw.textbbox((0, 0), line, font=f)[2] for line in lines]
        if max(widths) <= max_width:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def draw_outlined_line(img, text, center_x, top_y, font, fill):
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = center_x - w / 2 - bbox[0]
    y = top_y - bbox[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=10, stroke_fill=(0, 0, 0, 255))
    return bbox[3] - bbox[1]


def make_thumb(base_name: str, crop_x0: int | None, line1: str, line2: str, out_name: str) -> None:
    img = load_cropped_base(base_name, crop_x0)

    font = fit_font_for_lines([line1, line2], max_width=960)

    top_y = 50
    line_gap = 16
    h1 = draw_outlined_line(img, line1, W // 2, top_y, font, WHITE)
    draw_outlined_line(img, line2, W // 2, top_y + h1 + line_gap, font, GOLD)

    out = img.convert("RGB")
    path = OUT / out_name
    out.save(path, "PNG", optimize=True)
    print(f"{path.name}: {path.stat().st_size / 1024:.1f} KB")

    small = out.resize((270, 480), Image.LANCZOS)
    small.save(path.with_name(path.stem + "_check.png"))


if __name__ == "__main__":
    # short1: base-A.png（1672x941）。手元のスマホ画面（およそ x830-1080）を優先し、
    # 後ろ姿の頭部右端（およそ x=560）から右をクロップ幅529pxで取る。
    make_thumb("base-A.png", 460, "なぜ冷笑して", "しまうのか？", "short1-thumb.png")

    # short2: base-C.png（1672x941）。古代の柱がほぼ画面中央にあるため中央クロップ。
    make_thumb("base-C.png", None, "犬は権力に吠え", "冷笑は本気に吠える", "short2-thumb.png")
