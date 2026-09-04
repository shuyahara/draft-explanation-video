"""ずんだ人文学 チャンネルアイコン v3（ユーザー提供の実素材を切り抜いて使う版）。

ユーザーが持ち込んだ1枚の画像（角帽＋丸眼鏡＋口髭のセット、黒シルエット・白背景・JPEG）から
3パーツを切り抜き・透過化したものを合成する。切り抜き自体は
`C:\\Users\\shuya\\AppData\\Local\\Temp\\claude\\...\\scratchpad\\prep_user_parts.py`
（一回限りの前処理、実行済み）で行い、`assets-kamishibai/icon-parts/user-cap.png` /
`user-glasses.png` / `user-mustache.png` として保存済み。本スクリプトはその3パーツを
ずんだもんの立ち絵に合成するだけを担当する。

顔ランドマーク・黒板背景・白縁・800x800キャンバス・円形プレビューの生成ロジックは
v1/v2（`make_icon.py` / `make_icon2.py`）と共通のものを再利用する。

出力: icon3-1.png / icon3-1-circle.png（表情 smug）
      icon3-2.png / icon3-2-circle.png（表情 normal）

実行: script-to-video の venv の python で実行すること。
    C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe make_icon3.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

import make_icon as v1
import make_icon2 as v2  # place_part（アンカー合わせの拡縮合成）を再利用

PARTS_DIR = Path(r"C:\Users\shuya\Projects\assets-kamishibai\icon-parts")
OUT_DIR = Path(__file__).parent
CANVAS = v1.CANVAS
TOP_MARGIN = v1.TOP_MARGIN


def load_part(filename: str) -> Image.Image:
    return Image.open(PARTS_DIR / filename).convert("RGBA")


# ------------------------------------------------------------------
# パーツのアンカー座標（各パーツ画像のローカル座標系。prep_user_parts.py の実測値に基づく）
# ------------------------------------------------------------------

# 角帽（user-cap.png はクロップのオフセットが (0,0) なので元画像の座標そのまま使える）。
# アンカー = ドーム下端の中心（頭に接する点）。
CAP_SRC = "user-cap.png"
CAP_ANCHOR = (739, 848)
CAP_TARGET = (v1.HAT_CX, 125)
CAP_SCALE = 0.17  # ドームが縦に長い意匠のため v1/v2 の板幅(340px)より小さめに調整

# 丸眼鏡（user-glasses.png のローカル座標）。アンカー = 左右レンズ中心の中点。
GLASSES_SRC = "user-glasses.png"
GLASSES_ANCHOR = (410, 161)
GLASSES_LENS_SEP_SRC = 608 - 212
GLASSES_TARGET = ((v1.EYE_L[0] + v1.EYE_R[0]) / 2, (v1.EYE_L[1] + v1.EYE_R[1]) / 2)
GLASSES_SCALE = (v1.EYE_R[0] - v1.EYE_L[0]) / GLASSES_LENS_SEP_SRC

# 口髭（user-mustache.png のローカル座標）。アンカー = アーチ頂点（上端中央）。
# 口を覆う前提の形なので、口のやや上に頂点を置く。
MUSTACHE_SRC = "user-mustache.png"
MUSTACHE_ANCHOR = (305, 3)
MUSTACHE_TARGET = (v1.FACE_CX, v1.MOUTH[1] - 20)
MUSTACHE_SCALE = 210 / 611


def compose_character(
    expr: str,
    *,
    cap_scale: float = CAP_SCALE,
    cap_target: tuple[float, float] = CAP_TARGET,
) -> tuple[Image.Image, tuple[int, int], tuple[int, int]]:
    sprite = v1.load_sprite(expr)
    ext_size = (sprite.width, sprite.height + TOP_MARGIN)
    extended = Image.new("RGBA", ext_size, (0, 0, 0, 0))
    extended.alpha_composite(sprite, (0, TOP_MARGIN))

    cap_img = load_part(CAP_SRC)
    v2.place_part(extended, cap_img, CAP_ANCHOR, cap_target, cap_scale)

    glasses_img = load_part(GLASSES_SRC)
    v2.place_part(extended, glasses_img, GLASSES_ANCHOR, GLASSES_TARGET, GLASSES_SCALE)

    mustache_img = load_part(MUSTACHE_SRC)
    v2.place_part(extended, mustache_img, MUSTACHE_ANCHOR, MUSTACHE_TARGET, MUSTACHE_SCALE)

    outlined = v1.add_paper_outline(extended, outline_px=12)
    return outlined, extended.size, outlined.size


def build_icon(
    name: str,
    expr: str,
    bg: Image.Image,
    *,
    cap_scale: float = CAP_SCALE,
    cap_target: tuple[float, float] = CAP_TARGET,
) -> Image.Image:
    outlined, comp_size, outlined_size = compose_character(expr, cap_scale=cap_scale, cap_target=cap_target)
    pad = (outlined_size[0] - comp_size[0]) // 2

    scale = v1.T_SCALE
    resized = outlined.resize(
        (round(outlined_size[0] * scale), round(outlined_size[1] * scale)), Image.LANCZOS
    )
    src_x = (v1.T_SRC[0] + pad) * scale
    src_y = (v1.T_SRC[1] + TOP_MARGIN + pad) * scale
    paste_x = round(v1.T_DST[0] - src_x)
    paste_y = round(v1.T_DST[1] - src_y)

    canvas = bg.convert("RGBA").copy()
    canvas.alpha_composite(resized, (paste_x, paste_y))
    rgb = canvas.convert("RGB")
    rgb.save(OUT_DIR / f"{name}.png")

    mask = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, CANVAS, CANVAS), fill=255)
    circle = canvas.copy()
    circle.putalpha(mask)
    circle.save(OUT_DIR / f"{name}-circle.png")
    return rgb


# icon3-3: 角帽を大きくした版（コーディネーター指示 2026-09-05）。
# 枝豆の飾りの間に収まる範囲で最大にするため板幅を v1/v2 相当（340px）に近づけつつ、
# 最終キャンバスの上端で頂点が切れないよう合わせ先 y も下げた。
CAP_SCALE_LARGE = 0.25
CAP_TARGET_LARGE = (v1.HAT_CX, 180)


def main() -> None:
    bg = v1.board_background(CANVAS)
    build_icon("icon3-1", "smug", bg)
    build_icon("icon3-2", "normal", bg)
    build_icon("icon3-3", "smug", bg, cap_scale=CAP_SCALE_LARGE, cap_target=CAP_TARGET_LARGE)
    print("done")


if __name__ == "__main__":
    main()
