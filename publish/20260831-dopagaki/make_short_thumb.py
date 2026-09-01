# -*- coding: utf-8 -*-
"""ドパガキショート1の縦サムネ（1080x1920）を合成する使い捨てスクリプト。2026-09-01。

publish/20260827-cynicism/make_short_thumbs.py を流用。ただし冷笑ショートのbase-A.pngと
異なり、素材の thumb-A.png（1280x720）は本編サムネとしてタイトル文字が既に焼き込み済み
（publish/20260831-dopagaki/make_thumbs.py 参照）。9:16へ単純クロップすると文字か被写体の
どちらかが大きく欠けるため、ここでは build.py の縦組み手法（ぼかし背景＋中央フィット）を
Pillowで再現し、thumb-A.pngの構図・文字をそのまま維持して縦1080x1920へ合成する
（新規テキストは追加しない＝台本正本の文言を変えない）。
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

SRC = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260831-dopagaki/thumb-A.png")
OUT = Path(r"C:/Users/shuya/Projects/draft-explanation-video/publish/20260831-dopagaki/short1-thumb.png")

W, H = 1080, 1920


def make_short_thumb() -> None:
    base = Image.open(SRC).convert("RGB")

    # 背景: 1080x1920を覆うようにスケール+中央クロップしてからぼかし・減光（build.pyの
    # boxblur=luma_radius=24 + eq=brightness=-0.14:saturation=0.55 相当をPillowで再現）。
    bw, bh = base.size
    scale = max(W / bw, H / bh)
    rw, rh = round(bw * scale), round(bh * scale)
    bg = base.resize((rw, rh), Image.LANCZOS)
    x0 = (rw - W) // 2
    y0 = (rh - H) // 2
    bg = bg.crop((x0, y0, x0 + W, y0 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=24))
    bg = ImageEnhance.Brightness(bg).enhance(0.86)
    bg = ImageEnhance.Color(bg).enhance(0.55)

    # 前景: 幅1080へフィットさせ、縦方向中央に配置。
    fw = W
    fh = round(bh * (fw / bw))
    fg = base.resize((fw, fh), Image.LANCZOS)

    canvas = bg.copy()
    canvas.paste(fg, (0, (H - fh) // 2))

    canvas.save(OUT, "PNG", optimize=True)
    print(f"{OUT.name}: {OUT.stat().st_size / 1024:.1f} KB")

    small = canvas.resize((270, 480), Image.LANCZOS)
    small.save(OUT.with_name(OUT.stem + "_check.png"))


if __name__ == "__main__":
    make_short_thumb()
