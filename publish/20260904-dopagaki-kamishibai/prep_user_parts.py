"""ユーザー提供の角帽+丸眼鏡+口髭セット画像を3パーツへ切り分ける前処理スクリプト（一回限り）。

入力: assets-kamishibai/icon-parts/user-set-original.jpg (1480x1440, 白背景に黒シルエット)
出力: assets-kamishibai/icon-parts/user-cap.png / user-glasses.png / user-mustache.png
"""
from __future__ import annotations
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SRC = Path(r"C:\Users\shuya\Projects\assets-kamishibai\icon-parts\user-set-original.jpg")
OUT_DIR = Path(r"C:\Users\shuya\Projects\assets-kamishibai\icon-parts")
DEBUG_DIR = OUT_DIR / "_debug"  # 中間確認用の副産物（アルファのみ・フチ抜き前など）。削除してよい
DEBUG_DIR.mkdir(exist_ok=True)

im = Image.open(SRC).convert("RGB")
arr = np.array(im).astype(np.float32)
H, W = arr.shape[:2]
print("size", W, H)

# ------------------------------------------------------------------
# 1) ウォーターマーク除去: 帽子のバウンディングボックス内（ボード＋ドーム。タッセルの
#    垂れ下がり部分は含まない矩形）で、黒でも白でもない中間グレーを黒に塗りつぶす。
# ------------------------------------------------------------------
CAP_BBOX = (0, 0, W, 848)  # x0,y0,x1,y1（848 はドーム下端。行方向の空白ギャップから実測）
L = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
bbox_mask = np.zeros((H, W), dtype=bool)
x0, y0, x1, y1 = CAP_BBOX
bbox_mask[y0:y1, x0:x1] = True
gray_mask = bbox_mask & (L >= 40) & (L <= 222)
print("gray(watermark) pixels fixed:", gray_mask.sum())
arr[gray_mask] = 0.0

# ------------------------------------------------------------------
# 2) 透過化: 明度から滑らかなアルファを作る（JPEG のノイズ・境界のギザギザ対策で
#    LOW〜HIGH の間をグラデーションにする）。
# ------------------------------------------------------------------
L2 = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
LOW, HIGH = 120.0, 210.0
alpha = np.clip((HIGH - L2) / (HIGH - LOW), 0.0, 1.0) * 255.0
alpha_arr = alpha.astype(np.uint8)

Image.fromarray(alpha_arr, "L").save(DEBUG_DIR / "_full_alpha_debug.png")

# ------------------------------------------------------------------
# 3) パーツ分割（実測した行・列の空白ギャップに基づく矩形＋マスク）
# ------------------------------------------------------------------
DOME_BOTTOM = 850          # 帽子（ボード+ドーム）と眼鏡/髭の間の空白ギャップ
TASSEL_X0, TASSEL_X1 = 1145, 1310  # ドーム下端より下で垂れるタッセルの列範囲（実測1166-1286+余白）
CUT_Y = 1150               # 眼鏡と口髭の境界（実測で完全な空白行は無かったため目視で決定）
MID_X0, MID_X1 = 300, 1160  # 眼鏡・口髭が収まる列範囲

# --- 角帽（ドーム+ボード全体 ∪ タッセルの垂れ下がり部分） ---
cap_mask = np.zeros((H, W), dtype=bool)
cap_mask[0:DOME_BOTTOM, :] = True
cap_mask[DOME_BOTTOM:H, TASSEL_X0:TASSEL_X1] = True
cap_alpha = np.where(cap_mask, alpha_arr, 0).astype(np.uint8)

# --- 丸眼鏡 ---
glasses_mask = np.zeros((H, W), dtype=bool)
glasses_mask[DOME_BOTTOM:CUT_Y, MID_X0:MID_X1] = True
glasses_alpha = np.where(glasses_mask, alpha_arr, 0).astype(np.uint8)

# --- 口髭（下段） ---
mustache_mask = np.zeros((H, W), dtype=bool)
mustache_mask[CUT_Y:H, MID_X0:MID_X1] = True
mustache_alpha = np.where(mustache_mask, alpha_arr, 0).astype(np.uint8)
# CUT_Y 直下は眼鏡フレーム下端の破片が数十pxだけ残る（実測 y<1180 で run 数が不安定）。
# アーチの頂点だけが残るよう、中央の狭い帯だけ残して左右の破片を消す。
FRAG_TOP, FRAG_BOTTOM = CUT_Y, 1171
FRAG_KEEP_X0, FRAG_KEEP_X1 = 650, 850
mustache_alpha[FRAG_TOP:FRAG_BOTTOM, :FRAG_KEEP_X0] = 0
mustache_alpha[FRAG_TOP:FRAG_BOTTOM, FRAG_KEEP_X1:] = 0


def crop_to_content(alpha_channel: np.ndarray, pad: int = 12) -> tuple[Image.Image, tuple[int, int, int, int]]:
    ys, xs = np.where(alpha_channel > 8)
    bx0, bx1 = max(0, xs.min() - pad), min(W, xs.max() + pad + 1)
    by0, by1 = max(0, ys.min() - pad), min(H, ys.max() + pad + 1)
    crop_alpha = alpha_channel[by0:by1, bx0:bx1]
    rgba = np.zeros((*crop_alpha.shape, 4), dtype=np.uint8)
    rgba[..., 3] = crop_alpha
    print("bbox", bx0, by0, bx1, by1, "size", bx1 - bx0, by1 - by0)
    return Image.fromarray(rgba, "RGBA"), (bx0, by0, bx1, by1)


print("--- cap ---")
cap_img, _ = crop_to_content(cap_alpha)
cap_img.save(OUT_DIR / "user-cap.png")

print("--- glasses ---")
glasses_img, _ = crop_to_content(glasses_alpha)
glasses_img.save(OUT_DIR / "user-glasses.png")

print("--- mustache (before white fill) ---")
mustache_img, mbox = crop_to_content(mustache_alpha)
mbx0, mby0, mbx1, mby1 = mbox
mustache_img.save(DEBUG_DIR / "_mustache_outline_only.png")

# ------------------------------------------------------------------
# 4) 口髭の内側を白で塗りつぶす。
#
#    アーチ部分（膨らんだ上側、中に囲まれた白い内側がある）と、下側の歯（scallop）部分は
#    別々に扱う: 歯の部分は元々ベタ塗りの黒（塗りつぶし不要）で、しかも画像の下端で
#    切れているため、歯を含めた全体を素朴にフラッドフィルすると背景全体に漏れる。
#    アーチの内側だけを対象にフラッドフィルし、歯の部分は元のアルファをそのまま使う。
# ------------------------------------------------------------------
BELLY_TOP, BELLY_BOTTOM = 1150, 1375  # 実測: y<1375 は「アーチ2本足」、y>=1380 で歯が始まる

# 口髭クロップ内のローカル座標に変換
belly_top_local = max(0, BELLY_TOP - mby0)
belly_bottom_local = min(mustache_img.height, BELLY_BOTTOM - mby0)

mustache_arr = np.array(mustache_img)
belly_slice = mustache_arr[belly_top_local:belly_bottom_local, :, :].copy()
belly_img = Image.fromarray(belly_slice, "RGBA").copy()  # .copy() は floodfill が fromarray 直後だと無効になる PIL の挙動への対処
bw, bh = belly_img.size
seed = (bw // 2, bh - 20)
print("belly size", bw, bh, "seed", seed, "seed alpha", belly_img.getpixel(seed))
ImageDraw.floodfill(belly_img, seed, (255, 255, 255, 255), thresh=10)
belly_filled_arr = np.array(belly_img)

# 漏れチェック（左右端に白が付いていないか＝アーチの脚で正しく閉じているか）
leak_lr = belly_filled_arr[:, 0, 3].max() > 0 or belly_filled_arr[:, -1, 3].max() > 0
print("belly left/right leak:", leak_lr)

final_arr = mustache_arr.copy()
final_arr[belly_top_local:belly_bottom_local, :, :] = belly_filled_arr

final_img = Image.fromarray(final_arr, "RGBA")
final_img.save(OUT_DIR / "user-mustache.png")
print("mustache final size", final_img.size)
print("done")
