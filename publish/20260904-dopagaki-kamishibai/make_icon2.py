"""ずんだ人文学 チャンネルアイコン v2（フリー素材の透過 PNG を合成する版）。

v1（make_icon.py）は Pillow の図形描画で小物を手描きしたが、ユーザー FB により
「手描きの小物には納得していない。角帽・丸眼鏡・ひげはネットのフリー素材を拾って
付けるのがよい」との方針変更を受けて作り直したもの。

小物はすべて Pixabay Content License（商用可・帰属表記不要）または Openclipart
（CC0 / Public Domain）の透過 PNG を使用。出典・作者・ライセンスは icon.md の表を参照。
入手元ファイルは `C:\\Users\\shuya\\Projects\\assets-kamishibai\\icon-parts\\`（Git 管理外）。

顔ランドマーク・背景・白縁・800x800・円形プレビューの生成は v1（make_icon.py）と共通の
ロジックを再利用する（`import make_icon as v1`）。

出力: icon2-1.png / icon2-2.png / icon2-3.png（800x800, RGB）
      icon2-N-circle.png（円形トリミングの検品用プレビュー、RGBA）

実行: script-to-video の venv の python で実行すること（Pillow + numpy あり）。
    C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe make_icon2.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import make_icon as v1  # TOP_MARGIN / T_SCALE / T_SRC / T_DST / 顔ランドマーク / 背景 / 縁取りを共有

PARTS_DIR = Path(r"C:\Users\shuya\Projects\assets-kamishibai\icon-parts")
OUT_DIR = Path(__file__).parent
CANVAS = v1.CANVAS
TOP_MARGIN = v1.TOP_MARGIN


# ------------------------------------------------------------------
# 素材の読み込み・加工
# ------------------------------------------------------------------


def load_part(filename: str) -> Image.Image:
    return Image.open(PARTS_DIR / filename).convert("RGBA")


def process_hat(img: Image.Image) -> Image.Image:
    """青い角帽クリップアート（Mohamed_hassan, Pixabay）を黒系に配色し直し、
    元画像に付いているドロップシャドウ（低アルファのぼかし）を取り除く。"""

    arr = np.array(img).astype(np.float32)
    r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]

    # ドロップシャドウは半透明のグレー/黒（アルファ約45/255）。実体（アルファ255付近）と
    # 縁のアンチエイリアス（アルファがなだらかに0へ落ちる数px）だけを残し、それ以外の
    # 半透明領域（影）は透明にする。
    shadow = (a > 0) & (a < 150)
    a2 = np.where(shadow, 0, a)

    # タッセルの黄色だけ金色として残し、それ以外（青い板・紺の帯・黒い輪郭線）は
    # 輝度を保ったまま黒系へ落とす（板と帯の明暗差はそのまま濃淡として残る）。
    yellowish = (r > 140) & (g > 140) & (b < 190) & ((r - b) > 30) & ((g - b) > 20)
    luminance = (0.3 * r + 0.59 * g + 0.11 * b) / 255.0
    dark = 10 + luminance * 38

    out = np.empty_like(arr)
    out[..., 0] = np.where(yellowish, 201, dark)
    out[..., 1] = np.where(yellowish, 162, dark)
    out[..., 2] = np.where(yellowish, 55, dark * 0.95)
    out[..., 3] = a2
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


GLASSES_CROP = (0, 980, 2000, 1600)
"""元画像 2000x1600 のうち、レンズ+ブリッジだけを残す範囲。元画像は誇張された
「宙に浮いた」つる（テンプル）が上へ大きく跳ね上がる意匠で、そのままだとキャラの
頭髪に木の枝のような黒い線が刺さって見えてしまうため、つるの大部分を切り落とす。"""


def process_glasses(img: Image.Image) -> Image.Image:
    """丸眼鏡クリップアート（pawnk, Openclipart）を加工する。

    (1) 誇張されたつる（テンプル）の大部分をトリミングし、レンズ＋ブリッジ＋短いつるの
        付け根だけを残す。
    (2) レンズ内側が不透明な白で塗られているため、白い塗りは透明にしてスプライトの目を
        透かして見せる。
    """

    img = img.crop(GLASSES_CROP)
    arr = np.array(img).astype(np.uint8)
    r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    white = (r > 235) & (g > 235) & (b > 235)
    out = arr.copy()
    out[..., 3] = np.where(white, 0, a)
    return Image.fromarray(out, "RGBA")


def add_outline_to_flat_shape(
    img: Image.Image,
    outline_px: int,
    fill_color: tuple[int, int, int, int],
    outline_color: tuple[int, int, int, int],
) -> Image.Image:
    """単色シルエット画像に、塗り色の変更＋外周への輪郭線を付け足す（あごひげ用）。

    素材はもともと単色ベタ塗り（輪郭線なし）なので、アルファを膨張させた範囲を
    outline_color で塗り、その上から元のシルエット形状を fill_color で重ねる。
    """

    alpha = img.split()[-1]
    kernel = outline_px * 2 + 1
    dilated = alpha.filter(ImageFilter.MaxFilter(kernel))

    canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
    canvas.paste(outline_color, (0, 0), dilated)
    fill_layer = Image.new("RGBA", img.size, fill_color)
    canvas.paste(fill_layer, (0, 0), alpha)
    return canvas


# ------------------------------------------------------------------
# 各パーツの素材・アンカー座標（グリッド画像を目視計測して確定。icon.md に記録）
# ------------------------------------------------------------------

# 角帽（Mohamed_hassan, Pixabay #2298201）。アンカー = 帽体の開口部（頭が入る部分）の中心。
HAT_SRC = "hat-pixabay-2298201.png"
HAT_ANCHOR = (615, 830)
HAT_TARGET = (v1.HAT_CX, 115)
HAT_SCALE = 340 / 1030  # 板の対角幅を旧版と同程度（sprite 空間で約340px）に合わせる

# 丸眼鏡（pawnk, Openclipart #275579）。アンカー = 左右レンズ中心の中点（GLASSES_CROP で
# 切り出した後の座標系。元画像では (900, 1285)、クロップで y を 980 引いた値）。
GLASSES_SRC = "glasses-openclipart-275579.png"
GLASSES_ANCHOR = (900, 1285 - 980)
GLASSES_LENS_SEP_SRC = 1400 - 400  # 左右レンズ中心の距離（元画像・クロップの影響を受けない）
GLASSES_TARGET = ((v1.EYE_L[0] + v1.EYE_R[0]) / 2, (v1.EYE_L[1] + v1.EYE_R[1]) / 2)
GLASSES_SCALE = (v1.EYE_R[0] - v1.EYE_L[0]) / GLASSES_LENS_SEP_SRC

# 口髭（GDJ, Openclipart #237353）。アンカー = 上端中央の谷（鼻の下に当たる点）。
MUSTACHE_SRC = "mustache-openclipart-237353.png"
MUSTACHE_ANCHOR = (930, 45)
MUSTACHE_TARGET = (v1.FACE_CX, v1.MOUTH[1] - 14)
MUSTACHE_SCALE = 100 / 1867  # 顔幅に対して控えめな小ささ（ちょび髭寄りにするため）

# あごひげ（dear_theophilus, Openclipart #233589 の「goatee silhouette」からひげ部分のみ切り出し）。
# アンカー = 素材内の「口の穴」の中心。スプライト側の口の位置にこの穴を重ねることで、
# スプライト自身の口がそのまま透けて見える（穴がずれると首元が透けて見えてしまうため要注意）。
BEARD_SRC = "beard-openclipart-233589-crop.png"
BEARD_ANCHOR = (335, 125)
BEARD_TARGET = v1.MOUTH
BEARD_SCALE = 250 / 600
BEARD_OUTLINE_PX = 14  # 元画像解像度での輪郭線の太さ（BEARD_SCALE を掛けた後 ≒ 5〜6px）


def place_part(
    base: Image.Image,
    part: Image.Image,
    anchor_src: tuple[float, float],
    target_sprite_xy: tuple[float, float],
    scale: float,
) -> None:
    """パーツ画像を anchor_src が target_sprite_xy に来るように拡縮して base（拡張済み
    スプライト、TOP_MARGIN 分だけ上に余白がある座標系）へ合成する。"""

    new_size = (max(1, round(part.width * scale)), max(1, round(part.height * scale)))
    resized = part.resize(new_size, Image.LANCZOS)
    anchor_x = anchor_src[0] * scale
    anchor_y = anchor_src[1] * scale
    target_x, target_y_ext = target_sprite_xy[0], target_sprite_xy[1] + TOP_MARGIN
    paste_x = round(target_x - anchor_x)
    paste_y = round(target_y_ext - anchor_y)
    base.alpha_composite(resized, (paste_x, paste_y))


# ------------------------------------------------------------------
# 合成
# ------------------------------------------------------------------


def compose_character(expr: str, *, hat: bool, beard: bool) -> tuple[Image.Image, tuple[int, int], tuple[int, int]]:
    sprite = v1.load_sprite(expr)
    ext_size = (sprite.width, sprite.height + TOP_MARGIN)
    extended = Image.new("RGBA", ext_size, (0, 0, 0, 0))
    extended.alpha_composite(sprite, (0, TOP_MARGIN))

    if hat:
        hat_img = process_hat(load_part(HAT_SRC))
        place_part(extended, hat_img, HAT_ANCHOR, HAT_TARGET, HAT_SCALE)

    glasses_img = process_glasses(load_part(GLASSES_SRC))
    place_part(extended, glasses_img, GLASSES_ANCHOR, GLASSES_TARGET, GLASSES_SCALE)

    if beard:
        beard_raw = load_part(BEARD_SRC)
        beard_img = add_outline_to_flat_shape(
            beard_raw,
            BEARD_OUTLINE_PX,
            fill_color=(250, 248, 242, 255),
            outline_color=(70, 60, 50, 255),
        )
        place_part(extended, beard_img, BEARD_ANCHOR, BEARD_TARGET, BEARD_SCALE)
    else:
        mustache_img = load_part(MUSTACHE_SRC)
        place_part(extended, mustache_img, MUSTACHE_ANCHOR, MUSTACHE_TARGET, MUSTACHE_SCALE)

    outlined = v1.add_paper_outline(extended, outline_px=12)
    return outlined, extended.size, outlined.size


def build_icon(name: str, expr: str, *, hat: bool, beard: bool, bg: Image.Image) -> Image.Image:
    outlined, comp_size, outlined_size = compose_character(expr, hat=hat, beard=beard)
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


def main() -> None:
    bg = v1.board_background(CANVAS)

    # (1) 角帽＋丸眼鏡＋口髭
    build_icon("icon2-1", "smug", hat=True, beard=False, bg=bg)
    # (2) 角帽＋丸眼鏡＋白いあごひげ
    build_icon("icon2-2", "smug", hat=True, beard=True, bg=bg)
    # (3) 眼鏡と口髭だけ（帽子なし）
    build_icon("icon2-3", "normal", hat=False, beard=False, bg=bg)

    print("done")


if __name__ == "__main__":
    main()
