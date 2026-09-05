"""ずんだ人文学 チャンネルアイコン生成。

コンセプト: ずんだもんの公式立ち絵（坂本アヒル氏、改変可）の顔はそのまま使い、
Pillow で描いた小物（学者帽・眼鏡・髭）を重ねる。生成AIは使わない。

出力: icon-1.png / icon-2.png / icon-3.png（800x800, RGB）
      icon-1-circle.png 等（円形トリミングの検品用プレビュー、RGBA）

実行: script-to-video の venv の python で実行すること（Pillow あり）。
    C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe make_icon.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\shuya\Projects\script-to-video\src")

from PIL import Image, ImageDraw, ImageFilter

from script_to_video.kamishibai import add_paper_outline, compute_stage, render_board_plate
from script_to_video.schema import Kamishibai

SPRITES_DIR = Path(r"C:\Users\shuya\Projects\assets-kamishibai\sprites\zundamon")
OUT_DIR = Path(__file__).parent

SS = 4  # スーパーサンプリング倍率（小物を4倍解像度で描いてから縮小する）
CANVAS = 800
TOP_MARGIN = 230  # 帽子の頂点は元スプライトの y<0 にはみ出すため、上に余白を足してから描く
# （v3 のユーザー提供角帽はアンカーから頂点までが約195 sprite-px あり、160 では足りず
#   クリップされたため 230 に拡張。v1/v2 の帽子は元々 160 で収まっていたので後方互換）

# ------------------------------------------------------------------
# 顔ランドマーク（smug.png / normal.png 系、823x1513 の元画像座標系）
# _grid_*.png で目視計測して確定した値（本スクリプト実行後に削除してよい副産物）。
# ------------------------------------------------------------------
EYE_L = (237, 325)  # 画面向かって左目
EYE_R = (432, 320)  # 画面向かって右目
EYE_RADIUS_BASE = 58
FACE_CX = 345  # 顔の中心線（口・顎の中心 x）
MOUTH = (345, 403)
CHIN = (345, 438)
HAT_CX = 350  # 頭頂（アンテナの谷間、帽子を置く位置）の中心 x
HAT_REST_Y = 90  # 帽子の帯（バンド）が頭に接する y

# 最終キャンバスへの変換（顎を (400,560) 付近に、頭頂の帽子がキャンバス内に収まるように）
T_SCALE = 1.154
T_SRC = (FACE_CX, CHIN[1])
T_DST = (400, 560)


def to_canvas(pt: tuple[float, float]) -> tuple[float, float]:
    x, y = pt
    return (
        (x - T_SRC[0]) * T_SCALE + T_DST[0],
        (y - T_SRC[1]) * T_SCALE + T_DST[1],
    )


def s(pt: tuple[float, float]) -> tuple[int, int]:
    """小物レイヤー座標に変換（上に TOP_MARGIN ぶん広げた座標系 × SS 倍解像度）。"""
    return (round(pt[0] * SS), round((pt[1] + TOP_MARGIN) * SS))


def load_sprite(expr: str) -> Image.Image:
    return Image.open(SPRITES_DIR / f"{expr}.png").convert("RGBA")


def new_accessory_layer(base_size: tuple[int, int]) -> Image.Image:
    return Image.new("RGBA", (base_size[0] * SS, base_size[1] * SS), (0, 0, 0, 0))


def downscale_layer(layer: Image.Image, base_size: tuple[int, int]) -> Image.Image:
    return layer.resize(base_size, Image.LANCZOS)


# ------------------------------------------------------------------
# 小物パーツ
# ------------------------------------------------------------------

INK = (26, 24, 22, 255)
GOLD = (201, 162, 55, 255)
GOLD_DARK = (150, 118, 36, 255)
WHITE_FUR = (250, 248, 242, 255)
LENS_TINT = (235, 245, 248, 130)


def draw_mortarboard(d: ImageDraw.ImageDraw) -> None:
    """角帽（案1・案3共通）: 頭に沿う黒い帽体 + 菱形の板 + 金タッセル。"""

    cx, band_y = HAT_CX, HAT_REST_Y
    # 帽体（頭に沿う丸みのある帯）
    band_box = (
        s((cx - 135, band_y - 55)),
        s((cx + 135, band_y + 45)),
    )
    d.ellipse([*band_box[0], *band_box[1]], fill=INK, outline=(10, 10, 10, 255), width=4 * SS)

    # 菱形の板（頭より一回り大きい平たい板を上に乗せる）
    top_y = band_y - 60
    diamond = [
        s((cx, top_y - 55)),
        s((cx + 170, top_y)),
        s((cx, top_y + 55)),
        s((cx - 170, top_y)),
    ]
    d.polygon(diamond, fill=INK, outline=(10, 10, 10, 255))
    d.line([*diamond, diamond[0]], fill=(10, 10, 10, 255), width=4 * SS, joint="curve")
    # 板のハイライト（薄い反射線）
    d.line([s((cx - 60, top_y - 12)), s((cx + 40, top_y - 42))], fill=(70, 70, 70, 180), width=3 * SS)

    # ボタン（金）
    d.ellipse(
        [*s((cx - 11, top_y - 11)), *s((cx + 11, top_y + 11))],
        fill=GOLD, outline=GOLD_DARK, width=2 * SS,
    )

    # タッセルの紐（ボタンから右下へ垂らす）
    cord = [s((cx, top_y)), s((cx + 55, top_y + 55)), s((cx + 78, top_y + 110))]
    d.line(cord, fill=GOLD, width=4 * SS, joint="curve")
    # 房（先端の小さな束）
    tuft_cx, tuft_cy = cx + 78, top_y + 110
    for dx in (-10, -3, 4, 11):
        d.line(
            [s((tuft_cx + dx, tuft_cy)), s((tuft_cx + dx * 1.4, tuft_cy + 26))],
            fill=GOLD_DARK, width=3 * SS,
        )
    d.ellipse(
        [*s((tuft_cx - 12, tuft_cy - 8)), *s((tuft_cx + 12, tuft_cy + 8))],
        fill=GOLD, outline=GOLD_DARK, width=2 * SS,
    )


def draw_beret(d: ImageDraw.ImageDraw) -> None:
    """丸いドクターキャップ（案2）: ふくらんだ黒い丸帽 + 金の飾り。"""

    cx, band_y = HAT_CX, HAT_REST_Y
    # ふくらんだ丸帽本体（幅を絞って丸みを出す。キャンバス上端でクリップしない高さに収める）
    puff_box = [*s((cx - 130, band_y - 125)), *s((cx + 130, band_y + 15))]
    d.ellipse(puff_box, fill=INK, outline=(10, 10, 10, 255), width=4 * SS)
    # 頭に接する帯（すぼまり）
    band_box = [*s((cx - 130, band_y - 25)), *s((cx + 130, band_y + 45))]
    d.ellipse(band_box, fill=INK, outline=(10, 10, 10, 255), width=4 * SS)
    # ひだ（布のたるみを示す弧線。帽体下側の弧のみ＝ start/end は下半分の角度）
    for dx in (-70, -35, 0, 35, 70):
        d.arc(
            [*s((cx + dx - 42, band_y - 118)), *s((cx + dx + 42, band_y + 8))],
            start=20, end=160, fill=(60, 60, 60, 160), width=2 * SS,
        )
    # てっぺんの飾りボタン（金）
    top_cx, top_cy = cx, band_y - 118
    d.ellipse(
        [*s((top_cx - 13, top_cy - 13)), *s((top_cx + 13, top_cy + 13))],
        fill=GOLD, outline=GOLD_DARK, width=2 * SS,
    )


def draw_round_glasses(d: ImageDraw.ImageDraw) -> None:
    """丸眼鏡（案1・案3）: 細い黒フレーム、両目の中心に合わせる。"""

    r = EYE_RADIUS_BASE
    for cx, cy in (EYE_L, EYE_R):
        box = [*s((cx - r, cy - r)), *s((cx + r, cy + r))]
        d.ellipse(box, outline=INK, width=6 * SS, fill=LENS_TINT)
        # ハイライト線
        d.line(
            [s((cx - r * 0.45, cy - r * 0.55)), s((cx + r * 0.05, cy - r * 0.75))],
            fill=(255, 255, 255, 200), width=3 * SS,
        )
    # ブリッジ
    lx = EYE_L[0] + r
    rx = EYE_R[0] - r
    bridge_y = (EYE_L[1] + EYE_R[1]) / 2
    d.line([s((lx, EYE_L[1])), s((rx, EYE_R[1]))], fill=INK, width=6 * SS)
    # 左右のテンプル（つる）
    d.line([s((EYE_L[0] - r, EYE_L[1])), s((EYE_L[0] - r - 62, EYE_L[1] - 6))], fill=INK, width=6 * SS)
    d.line([s((EYE_R[0] + r, EYE_R[1])), s((EYE_R[0] + r + 62, EYE_R[1] - 8))], fill=INK, width=6 * SS)


def draw_halfmoon_glasses(d: ImageDraw.ImageDraw) -> None:
    """半月眼鏡（案2）: 少し下がった位置、金縁の下半分レンズ。"""

    r = EYE_RADIUS_BASE - 6
    drop = 22  # 目の中心より少し下げる
    centers = [(EYE_L[0], EYE_L[1] + drop), (EYE_R[0], EYE_R[1] + drop)]
    for cx, cy in centers:
        box = [*s((cx - r, cy - r)), *s((cx + r, cy + r))]
        d.chord(box, start=180, end=360, fill=LENS_TINT, outline=GOLD_DARK, width=5 * SS)
        d.line([s((cx - r, cy)), s((cx + r, cy))], fill=GOLD_DARK, width=4 * SS)
    lx, ly = centers[0]
    rx, ry = centers[1]
    d.line([s((lx + r, ly)), s((rx - r, ry))], fill=GOLD_DARK, width=5 * SS)
    d.line([s((lx - r, ly)), s((lx - r - 60, ly - 10))], fill=GOLD_DARK, width=5 * SS)
    d.line([s((rx + r, ry)), s((rx + r + 60, ry - 12))], fill=GOLD_DARK, width=5 * SS)


def draw_goatee(d: ImageDraw.ImageDraw) -> None:
    """白いあごひげ（案1）: 口を隠さず、顎の下に小さく沿わせる。"""

    top_y = MOUTH[1] + 14
    bottom_y = CHIN[1] + 42
    cx = FACE_CX
    pts = [
        s((cx - 45, top_y)),
        s((cx - 55, top_y + 30)),
        s((cx - 30, bottom_y)),
        s((cx, bottom_y + 12)),
        s((cx + 30, bottom_y)),
        s((cx + 55, top_y + 30)),
        s((cx + 45, top_y)),
        s((cx, top_y + 10)),
    ]
    d.polygon(pts, fill=WHITE_FUR, outline=(70, 70, 70, 255))


def _fluffy_blob(d: ImageDraw.ImageDraw, cx: float, cy: float, rx: float, ry: float, fill) -> None:
    """ふさふさ感を出すため、楕円の輪郭に沿って小さな円を連ねる。"""

    import math

    n = 14
    for i in range(n):
        a = math.pi * i / (n - 1)
        px = cx + rx * math.cos(math.pi - a)
        py = cy + ry * math.sin(a) * 0.9
        d.ellipse([*s((px - 14, py - 14)), *s((px + 14, py + 14))], fill=fill, outline=(70, 70, 70, 255))
    d.ellipse([*s((cx - rx, cy - ry)), *s((cx + rx, cy + ry))], fill=fill)


def draw_fluffy_mustache_beard(d: ImageDraw.ImageDraw) -> None:
    """白いふさふさの口髭＋あごひげ（案2）。"""

    cx = FACE_CX
    # 口髭（鼻の下、口の上に。normal.png は口が小さいので隠れすぎない）
    _fluffy_blob(d, cx, MOUTH[1] - 12, 78, 20, WHITE_FUR)
    # あごひげ（顎から頬にかけて）
    _fluffy_blob(d, cx, CHIN[1] + 50, 105, 55, WHITE_FUR)
    d.ellipse(
        [*s((cx - 105, CHIN[1] - 5)), *s((cx + 105, CHIN[1] + 100))],
        fill=WHITE_FUR,
    )


def draw_chevron_mustache(d: ImageDraw.ImageDraw) -> None:
    """小さな黒いちょび髭（案3）。口は隠さない。"""

    cx, my = FACE_CX, MOUTH[1] - 16
    pts = [
        s((cx - 42, my + 6)),
        s((cx - 20, my - 8)),
        s((cx, my - 2)),
        s((cx + 20, my - 8)),
        s((cx + 42, my + 6)),
        s((cx + 20, my + 10)),
        s((cx, my + 4)),
        s((cx - 20, my + 10)),
    ]
    d.polygon(pts, fill=(24, 22, 20, 255), outline=(10, 10, 10, 255))


# ------------------------------------------------------------------
# 合成
# ------------------------------------------------------------------


def compose_character(expr: str, hat: str, glasses: str, beard: str) -> Image.Image:
    sprite = load_sprite(expr)
    # 帽子の頂点が元スプライトの上端(y=0)より上にはみ出すため、上に TOP_MARGIN ぶんの
    # 透明な余白を持つ拡張キャンバスへ貼り直してから小物を描く。
    ext_size = (sprite.width, sprite.height + TOP_MARGIN)
    extended = Image.new("RGBA", ext_size, (0, 0, 0, 0))
    extended.alpha_composite(sprite, (0, TOP_MARGIN))

    layer = new_accessory_layer(ext_size)
    d = ImageDraw.Draw(layer)

    if hat == "mortarboard":
        draw_mortarboard(d)
    elif hat == "beret":
        draw_beret(d)

    if beard == "goatee":
        draw_goatee(d)
    elif beard == "fluffy":
        draw_fluffy_mustache_beard(d)
    elif beard == "chevron":
        draw_chevron_mustache(d)

    if glasses == "round":
        draw_round_glasses(d)
    elif glasses == "halfmoon":
        draw_halfmoon_glasses(d)

    accessory = downscale_layer(layer, ext_size)
    composite = Image.alpha_composite(extended, accessory)
    outlined = add_paper_outline(composite, outline_px=12)
    return outlined, composite.size, outlined.size


def board_background(size: int) -> Image.Image:
    """紙芝居の黒板と同じ下地から、無地に近い緑の黒板部分を正方形に切り出す。"""

    big = size * 2
    config = Kamishibai()
    stage = compute_stage(big, big, config)
    plate = render_board_plate(stage, config)
    bl, bt, br, bb = stage.board_rect
    bw, bh = br - bl, bb - bt
    side = min(bw, bh)
    cx, cy = (bl + br) // 2, (bt + bb) // 2
    crop = plate.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
    return crop.resize((size, size), Image.LANCZOS)


def build_icon(name: str, expr: str, hat: str, glasses: str, beard: str, bg: Image.Image) -> Image.Image:
    outlined, comp_size, outlined_size = compose_character(expr, hat, glasses, beard)
    pad = (outlined_size[0] - comp_size[0]) // 2  # add_paper_outline が全周に付けた縁の幅

    scale = T_SCALE
    resized = outlined.resize(
        (round(outlined_size[0] * scale), round(outlined_size[1] * scale)), Image.LANCZOS
    )
    # 元スプライト座標 T_SRC は outlined 画像内では (x+pad, y+TOP_MARGIN+pad) にある
    src_x = (T_SRC[0] + pad) * scale
    src_y = (T_SRC[1] + TOP_MARGIN + pad) * scale
    paste_x = round(T_DST[0] - src_x)
    paste_y = round(T_DST[1] - src_y)

    canvas = bg.convert("RGBA").copy()
    canvas.alpha_composite(resized, (paste_x, paste_y))
    rgb = canvas.convert("RGB")
    rgb.save(OUT_DIR / f"{name}.png")

    # 円形プレビュー
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, CANVAS, CANVAS), fill=255)
    circle = canvas.copy()
    circle.putalpha(mask)
    circle.save(OUT_DIR / f"{name}-circle.png")
    return rgb


def main() -> None:
    bg = board_background(CANVAS)

    build_icon("icon-1", "smug", "mortarboard", "round", "goatee", bg)
    build_icon("icon-2", "normal", "beret", "halfmoon", "fluffy", bg)
    build_icon("icon-3", "smug", "mortarboard", "round", "chevron", bg)

    print("done")


if __name__ == "__main__":
    main()
