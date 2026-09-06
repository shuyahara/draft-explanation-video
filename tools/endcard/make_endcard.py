"""チャンネル共通エンドカード（挨拶クリップ）を生成する。

YouTube チャンネル「ずんだ人文学」（四国めたん×ずんだもんの解説動画）向けに、
本編（緑の黒板の紙芝居モード）とは別の見た目を持つ、全動画共通の締めクリップを作る。
できあがった mp4 は script-to-video 側の `stv render --end-card <mp4>` で
本編末尾に結合する（endcard.py 参照）。

## 何をするか

1. チャンネルアイコンの外周ピクセルの中央値から背景色を決める（単色背景）。
2. 左に四国めたん、右にずんだもんの立ち絵（笑顔）を画面高 80% 程度で配置し、
   開始 0.4 秒で左右からスライドインさせる（本編の入場アニメと同じイージングを使う）。
3. VOICEVOX でナレーション3行を合成する（四国めたん=style2 / ずんだもん=style3、
   speedScale 1.1）。各行の実測尺から、上段見出し・3つのアイコン（高評価／
   チャンネル登録／コメント）の出現タイミングを合わせる。
4. Pillow で全フレームを合成し、rawvideo として ffmpeg にパイプして無音の映像を作る
   （script-to-video の kamishibai.py / render.py と同じ「毎フレーム純関数で描画→
   rawvideo pipe」の方式。この2ファイルには依存しない独立スクリプトとして書く）。
5. 音声（3行＋間0.5秒×2＋末尾ホールド2.5秒）を波形として合成し、映像と同じ尺に
   そろえる。
6. 映像・音声それぞれに最後の1.0秒でフェードアウトを掛けて結合し、
   `script_to_video.audio_mix.apply_bgm_and_loudnorm`（BGM無し呼び出し）で
   -14 LUFS に正規化する。

## 使い方

    C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe ^
        tools\\endcard\\make_endcard.py

- 事前に VOICEVOX ENGINE を起動しておくこと（既定 http://127.0.0.1:50021）。
- ffmpeg / ffprobe が PATH にあること（無ければ script_to_video.render の自動解決に従う）。
- 出力: C:\\Users\\shuya\\Projects\\assets-kamishibai\\endcard\\endcard.mp4
  （Git 管理外フォルダ）。中間ファイルは build/endcard-work/ に置く。
- 再実行すれば同じ入力（立ち絵・アイコン・VOICEVOX の応答）から同じ mp4 が作れる
  （本スクリプトの画面合成・タイミング計算はすべて音声の実測尺からの決定的な計算。
  乱数は使わない）。VOICEVOX 側の合成結果自体が変われば当然出力も変わる。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

# script-to-video のソースを import できるようにする（このスクリプトは
# draft-explanation-video リポジトリ側に置くが、実行は script-to-video の venv
# python で行う前提。sys.path 追加はその venv の site-packages に script_to_video が
# 無い場合の保険）。
_SCRIPT_TO_VIDEO_SRC = Path(r"C:\Users\shuya\Projects\script-to-video\src")
if str(_SCRIPT_TO_VIDEO_SRC) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_TO_VIDEO_SRC))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from script_to_video.audio_mix import AudioMixError, apply_bgm_and_loudnorm  # noqa: E402
from script_to_video.icons import ICON_FONT_PATH, resolve_icon_codepoint  # noqa: E402
from script_to_video.kamishibai import CHALK_FONT_CANDIDATES, ease_out_cubic  # noqa: E402
from script_to_video.render import resolve_ffmpeg_path, resolve_ffprobe_path  # noqa: E402
from script_to_video.tts import VoicevoxClient  # noqa: E402

# ============================================================
# パス定数
# ============================================================

ICON_PATH = Path(
    r"C:\Users\shuya\Projects\draft-explanation-video\publish\20260904-dopagaki-kamishibai\icon3-1.png"
)
METAN_SPRITE_PATH = Path(r"C:\Users\shuya\Projects\assets-kamishibai\sprites\metan\smile.png")
ZUNDAMON_SPRITE_PATH = Path(r"C:\Users\shuya\Projects\assets-kamishibai\sprites\zundamon\smile.png")

OUT_DIR = Path(r"C:\Users\shuya\Projects\assets-kamishibai\endcard")
OUT_PATH = OUT_DIR / "endcard.mp4"

WORK_DIR = Path(r"C:\Users\shuya\Projects\script-to-video\build\endcard-work")

# ============================================================
# 画面・タイミング定数
# ============================================================

WIDTH, HEIGHT, FPS = 1920, 1080, 30

METAN_STYLE_ID = 2
ZUNDAMON_STYLE_ID = 3
SPEED_SCALE = 1.1

LINE1_METAN = "今日はここまで。ご視聴ありがとうございました。"
LINE2_ZUNDAMON = "面白いと思ったら、高評価とチャンネル登録をお願いするのだ。"
LINE3_METAN = "それと、あなたの意見も、コメントで教えてね。"

GAP_SECONDS = 0.5
"""セリフ間の間（設計メモの「各行の間は0.5秒」）。"""

HOLD_SECONDS = 2.5
"""最後のセリフの後の保持時間。"""

FADE_SECONDS = 1.0
"""末尾フェードアウトの長さ（映像・音声とも）。"""

ENTRANCE_SECONDS = 0.4
"""立ち絵のスライドインにかける秒数（設計メモの指定値。本編 kamishibai.py の入場は
0.7秒だが、エンドカードは短尺のクリップなので指定どおり短くする）。"""

POP_SECONDS = 0.3
"""見出し・アイコンが現れるときのポップイン（拡大+フェードイン）の長さ。"""

SPRITE_HEIGHT_RATIO = 0.80
"""立ち絵の高さ（画面高に対する比）。"""

BOTTOM_MARGIN = 40
"""立ち絵の足元と画面下端の余白（px）。"""

LEFT_CENTER_X_RATIO = 0.24
RIGHT_CENTER_X_RATIO = 0.76

HEADLINE_TEXT = "ご視聴ありがとうございました"
HEADLINE_Y_RATIO = 0.10
HEADLINE_FONT_RATIO = 0.062

ICON_ROW_Y_RATIO = 0.47
"""アイコン行（丸アイコン＋短い文字）の中心 y（画面高に対する比）。左右の立ち絵の
あいだの余白に収める。"""

ICON_CIRCLE_DIAMETER_RATIO = 0.115
ICON_LABEL_FONT_RATIO = 0.028
ICON_COLUMN_GAP_RATIO = 0.03
"""アイコン列どうしの間隔（画面幅に対する比）。"""

CHALK_COLOR = (238, 236, 226)
"""本編の chalk 文字と同じ色（kamishibai.CHALK_COLOR）。文字色をそろえる。"""

ICON_VARIATION_AXES = (1, 0, 24, 500)
"""diagram.py の `_icon_font` と同じ可変軸設定（FILL=1 塗りつぶし・GRAD=0・opsz=24・wght=500）。"""

CIRCLE_ICONS: list[tuple[str, list[str]]] = [
    ("thumb_up", ["高評価"]),
    ("notifications", ["チャンネル", "登録"]),
    ("chat_bubble", ["コメント"]),
]
"""(アイコン名, ラベルの行のリスト)。「チャンネル登録」は横幅が広すぎて隣の列と
重なるため2行に分けて表示する。"""

ICON_LABEL_LINE_SPACING_RATIO = 0.010
"""ラベルが2行になる場合の行間（画面高に対する比）。"""

ICON_COLUMN_PADDING = 24
"""アイコン列の左右余白（px）。ラベル幅が円の直径より広い列の余白として使う。"""


# ============================================================
# 背景色（チャンネルアイコンの外周ピクセルの中央値）
# ============================================================


def sample_background_color(icon_path: Path) -> tuple[int, int, int]:
    """アイコン画像の外周1pxリングの中央値をRGBで返す。"""

    image = Image.open(icon_path).convert("RGB")
    width, height = image.size
    pixels = image.load()
    border: list[tuple[int, int, int]] = []
    for x in range(width):
        border.append(pixels[x, 0])
        border.append(pixels[x, height - 1])
    for y in range(height):
        border.append(pixels[0, y])
        border.append(pixels[width - 1, y])

    border.sort(key=lambda p: p[0])
    r = sorted(p[0] for p in border)[len(border) // 2]
    g = sorted(p[1] for p in border)[len(border) // 2]
    b = sorted(p[2] for p in border)[len(border) // 2]
    return (r, g, b)


def _blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
    )


# ============================================================
# フォント
# ============================================================


def resolve_chalk_font_path() -> Path:
    for path in CHALK_FONT_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(f"利用可能なフォントが見つかりません: {CHALK_FONT_CANDIDATES}")


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(resolve_chalk_font_path()), size)


def _load_icon_font(size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(ICON_FONT_PATH), size)
    font.set_variation_by_axes(list(ICON_VARIATION_AXES))
    return font


# ============================================================
# 立ち絵の読み込み（透過部分をトリムしてから高さを揃える）
# ============================================================


@dataclass(frozen=True)
class Sprite:
    image: Image.Image  # RGBA。トリム＋リサイズ済み
    final_x: int
    final_y: int
    off_x: int
    """スライドイン開始時（画面外）の x 座標。"""


def _load_sprite(path: Path, *, target_height: int) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    bbox = image.getbbox()
    if bbox is not None:
        image = image.crop(bbox)
    scale = target_height / image.height
    target_width = max(1, round(image.width * scale))
    return image.resize((target_width, target_height), Image.LANCZOS)


def build_sprites() -> tuple[Sprite, Sprite]:
    target_height = round(HEIGHT * SPRITE_HEIGHT_RATIO)
    metan_img = _load_sprite(METAN_SPRITE_PATH, target_height=target_height)
    zundamon_img = _load_sprite(ZUNDAMON_SPRITE_PATH, target_height=target_height)

    final_y = HEIGHT - BOTTOM_MARGIN - target_height

    metan_final_x = round(WIDTH * LEFT_CENTER_X_RATIO - metan_img.width / 2)
    zundamon_final_x = round(WIDTH * RIGHT_CENTER_X_RATIO - zundamon_img.width / 2)

    metan = Sprite(image=metan_img, final_x=metan_final_x, final_y=final_y, off_x=-metan_img.width)
    zundamon = Sprite(image=zundamon_img, final_x=zundamon_final_x, final_y=final_y, off_x=WIDTH)
    return metan, zundamon


# ============================================================
# アイコン行のレイアウト（円の直径 or ラベル幅の広い方に列幅を合わせる）
# ============================================================


@dataclass(frozen=True)
class IconColumn:
    icon_name: str
    label_lines: list[str]
    center_x: float
    """列の中心 x（画面座標）。"""
    width: int
    """この列のレイヤー幅（円とラベルの広い方＋余白）。"""
    height: int
    """この列のレイヤー高さ（円＋行間＋ラベル行数ぶん）。"""


def build_icon_columns(
    icon_label_font: ImageFont.FreeTypeFont, *, diameter: int, gap_left: float, gap_right: float
) -> list[IconColumn]:
    """3列ぶんの列幅を先に確定してから中心 x を割り振る（ラベルが円より広い列は
    その分だけ列幅を広げるので、`build_icon_columns` を呼んだ時点で列どうしが
    重ならないことが保証される）。
    """

    measure_image = Image.new("L", (1, 1))
    measure_draw = ImageDraw.Draw(measure_image)
    line_spacing = round(HEIGHT * ICON_LABEL_LINE_SPACING_RATIO)

    columns: list[IconColumn] = []
    for icon_name, label_lines in CIRCLE_ICONS:
        line_widths = []
        line_height = 0
        for line in label_lines:
            bbox = measure_draw.textbbox((0, 0), line, font=icon_label_font)
            line_widths.append(bbox[2] - bbox[0])
            line_height = max(line_height, bbox[3] - bbox[1])
        max_line_width = max(line_widths, default=0)
        width = max(diameter, max_line_width + ICON_COLUMN_PADDING * 2)
        label_block_height = len(label_lines) * line_height + max(0, len(label_lines) - 1) * line_spacing
        height = diameter + round(HEIGHT * 0.015) + label_block_height
        columns.append(IconColumn(icon_name=icon_name, label_lines=label_lines, center_x=0.0, width=width, height=height))

    column_gap = round(WIDTH * ICON_COLUMN_GAP_RATIO)
    total_row_width = sum(c.width for c in columns) + column_gap * (len(columns) - 1)
    gap_center = (gap_left + gap_right) / 2
    cursor = gap_center - total_row_width / 2
    resolved: list[IconColumn] = []
    for column in columns:
        center_x = cursor + column.width / 2
        resolved.append(
            IconColumn(
                icon_name=column.icon_name, label_lines=column.label_lines,
                center_x=center_x, width=column.width, height=column.height,
            )
        )
        cursor += column.width + column_gap
    return resolved


# ============================================================
# VOICEVOX 音声合成
# ============================================================


@dataclass(frozen=True)
class Line:
    text: str
    style_id: int
    pcm: bytes
    sample_rate: int
    duration: float


def synthesize_lines(client: VoicevoxClient) -> list[Line]:
    lines: list[Line] = []
    for text, style_id in (
        (LINE1_METAN, METAN_STYLE_ID),
        (LINE2_ZUNDAMON, ZUNDAMON_STYLE_ID),
        (LINE3_METAN, METAN_STYLE_ID),
    ):
        wav_bytes = client.synthesize_text(text, style_id)
        wav_path = WORK_DIR / f"_tmp_{style_id}_{len(lines)}.wav"
        wav_path.write_bytes(wav_bytes)
        with wave.open(str(wav_path), "rb") as wf:
            assert wf.getnchannels() == 1, f"想定外のチャンネル数: {wf.getnchannels()}"
            assert wf.getsampwidth() == 2, f"想定外のサンプル幅: {wf.getsampwidth()}"
            rate = wf.getframerate()
            pcm = wf.readframes(wf.getnframes())
        duration = len(pcm) / 2 / rate
        lines.append(Line(text=text, style_id=style_id, pcm=pcm, sample_rate=rate, duration=duration))
    return lines


def _silence_pcm(seconds: float, rate: int) -> bytes:
    n = max(0, round(seconds * rate))
    return b"\x00\x00" * n


@dataclass(frozen=True)
class Timeline:
    total_duration: float
    headline_appear: float
    icon_appear: list[float]
    """CIRCLE_ICONS と同じ順（高評価・チャンネル登録・コメント）。"""
    pcm: bytes
    sample_rate: int


def build_timeline(lines: list[Line]) -> Timeline:
    line1, line2, line3 = lines
    rate = line1.sample_rate
    assert line2.sample_rate == rate and line3.sample_rate == rate, "VOICEVOXの出力サンプルレートが話者間で異なります"

    t1_start = 0.0
    t1_end = t1_start + line1.duration
    t2_start = t1_end + GAP_SECONDS
    t2_end = t2_start + line2.duration
    t3_start = t2_end + GAP_SECONDS
    t3_end = t3_start + line3.duration
    audio_duration = t3_end + HOLD_SECONDS

    def _proportional(text: str, substring: str, seg_start: float, seg_duration: float) -> float:
        idx = text.index(substring)
        ratio = idx / len(text)
        return seg_start + ratio * seg_duration

    icon_appear = [
        _proportional(line2.text, "高評価", t2_start, line2.duration),
        _proportional(line2.text, "チャンネル登録", t2_start, line2.duration),
        _proportional(line3.text, "コメント", t3_start, line3.duration),
    ]

    pcm = b"".join(
        [
            line1.pcm,
            _silence_pcm(GAP_SECONDS, rate),
            line2.pcm,
            _silence_pcm(GAP_SECONDS, rate),
            line3.pcm,
            _silence_pcm(HOLD_SECONDS, rate),
        ]
    )

    # 映像はフレーム単位（1/FPS秒刻み）にしかならないので、映像の実尺
    # （round(audio_duration*FPS)/FPS）に音声の総サンプル数をそろえる（末尾ホールドの
    # 範囲内で無音を足し引きするだけなので、聴感には影響しない）。
    video_frame_count = round(audio_duration * FPS)
    video_duration = video_frame_count / FPS
    target_samples = round(video_duration * rate)
    current_samples = len(pcm) // 2
    if target_samples > current_samples:
        pcm += b"\x00\x00" * (target_samples - current_samples)
    elif target_samples < current_samples:
        pcm = pcm[: target_samples * 2]

    return Timeline(
        total_duration=video_duration,
        headline_appear=t1_start,
        icon_appear=icon_appear,
        pcm=pcm,
        sample_rate=rate,
    )


# ============================================================
# フレーム描画
# ============================================================


def _pop_progress(t: float, appear_at: float) -> tuple[float, float] | None:
    """(alpha, scale) を返す。まだ出現していなければ None。"""

    if t < appear_at:
        return None
    elapsed = t - appear_at
    if elapsed >= POP_SECONDS:
        return 1.0, 1.0
    p = ease_out_cubic(elapsed / POP_SECONDS)
    return p, 0.7 + 0.3 * p


def _paste_scaled(base: Image.Image, sprite: Image.Image, cx: float, cy: float, scale: float, alpha: float) -> None:
    """`sprite`（RGBA）を中心 (cx, cy) に scale 倍・alpha 掛けで貼る。"""

    if scale <= 0.0 or alpha <= 0.0:
        return
    w = max(1, round(sprite.width * scale))
    h = max(1, round(sprite.height * scale))
    resized = sprite.resize((w, h), Image.LANCZOS) if scale != 1.0 else sprite
    if alpha < 1.0:
        r, g, b, a = resized.split()
        a = a.point(lambda v: round(v * alpha))
        resized = Image.merge("RGBA", (r, g, b, a))
    base.alpha_composite(resized, (round(cx - w / 2), round(cy - h / 2)))


def render_frame(
    t: float,
    *,
    bg_color: tuple[int, int, int],
    metan: Sprite,
    zundamon: Sprite,
    timeline: Timeline,
    headline_font: ImageFont.FreeTypeFont,
    icon_label_font: ImageFont.FreeTypeFont,
    icon_glyph_font: ImageFont.FreeTypeFont,
    icon_columns: list[IconColumn],
    text_color: tuple[int, int, int],
    chip_color: tuple[int, int, int],
) -> Image.Image:
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (*bg_color, 255))
    draw = ImageDraw.Draw(frame)

    # --- 立ち絵（スライドイン） ---
    entrance_progress = ease_out_cubic(min(1.0, max(0.0, t / ENTRANCE_SECONDS)))
    for sprite in (metan, zundamon):
        x = round(sprite.off_x + (sprite.final_x - sprite.off_x) * entrance_progress)
        frame.alpha_composite(sprite.image, (x, sprite.final_y))

    # --- 見出し ---
    pop = _pop_progress(t, timeline.headline_appear)
    if pop is not None:
        alpha, scale = pop
        bbox = draw.textbbox((0, 0), HEADLINE_TEXT, font=headline_font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        headline_layer = Image.new("RGBA", (text_w + 20, text_h + 20), (0, 0, 0, 0))
        headline_draw = ImageDraw.Draw(headline_layer)
        headline_draw.text((10 - bbox[0], 10 - bbox[1]), HEADLINE_TEXT, font=headline_font, fill=(*text_color, 255))
        _paste_scaled(
            frame, headline_layer, WIDTH / 2, HEIGHT * HEADLINE_Y_RATIO, scale, alpha,
        )

    # --- アイコン行 ---
    diameter = round(HEIGHT * ICON_CIRCLE_DIAMETER_RATIO)
    icon_center_y = round(HEIGHT * ICON_ROW_Y_RATIO)
    line_spacing = round(HEIGHT * ICON_LABEL_LINE_SPACING_RATIO)

    for i, column in enumerate(icon_columns):
        pop = _pop_progress(t, timeline.icon_appear[i])
        if pop is None:
            continue
        alpha, scale = pop

        icon_layer = Image.new("RGBA", (column.width, column.height), (0, 0, 0, 0))
        icon_draw = ImageDraw.Draw(icon_layer)
        circle_left = column.width / 2 - diameter / 2
        icon_draw.ellipse((circle_left, 0, circle_left + diameter - 1, diameter - 1), fill=(*chip_color, 255))

        codepoint = resolve_icon_codepoint(column.icon_name)
        ch = chr(codepoint)
        glyph_bbox = icon_draw.textbbox((0, 0), ch, font=icon_glyph_font)
        glyph_w, glyph_h = glyph_bbox[2] - glyph_bbox[0], glyph_bbox[3] - glyph_bbox[1]
        icon_draw.text(
            (column.width / 2 - glyph_w / 2 - glyph_bbox[0], diameter / 2 - glyph_h / 2 - glyph_bbox[1]),
            ch, font=icon_glyph_font, fill=(*bg_color, 255),
        )

        label_y = diameter + round(HEIGHT * 0.015)
        for line in column.label_lines:
            label_bbox = icon_draw.textbbox((0, 0), line, font=icon_label_font)
            label_w, label_h = label_bbox[2] - label_bbox[0], label_bbox[3] - label_bbox[1]
            icon_draw.text(
                (column.width / 2 - label_w / 2 - label_bbox[0], label_y - label_bbox[1]),
                line, font=icon_label_font, fill=(*text_color, 255),
            )
            label_y += label_h + line_spacing

        column_center_y = icon_center_y - diameter / 2 + icon_layer.height / 2
        _paste_scaled(frame, icon_layer, column.center_x, column_center_y, scale, alpha)

    # --- 末尾フェードアウト（映像） ---
    fade_start = timeline.total_duration - FADE_SECONDS
    if t >= fade_start:
        fade = max(0.0, 1.0 - (t - fade_start) / FADE_SECONDS)
        rgb = frame.convert("RGB")
        black = Image.new("RGB", rgb.size, (0, 0, 0))
        return Image.blend(black, rgb, fade)

    return frame.convert("RGB")


def iter_frames(**kwargs):
    timeline: Timeline = kwargs["timeline"]
    frame_count = round(timeline.total_duration * FPS)
    for i in range(frame_count):
        t = i / FPS
        yield render_frame(t, **kwargs)


# ============================================================
# ffmpeg: 無音映像の書き出し
# ============================================================


def encode_silent_video(frames, *, frame_count: int, output_path: Path, ffmpeg_path: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_path, "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "pipe:0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(output_path),
    ]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    written = 0
    try:
        for frame in frames:
            proc.stdin.write(frame.tobytes())
            written += 1
        proc.stdin.close()
    except BrokenPipeError:
        pass
    _, stderr = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg（無音映像の書き出し）が失敗しました（終了コード{proc.returncode}）:\n"
                            f"{stderr.decode('utf-8', 'replace')}")
    if written < frame_count:
        raise RuntimeError(f"フレーム数が不足しています（書き出し={written} / 要求={frame_count}）")


def mux_video_and_audio(
    *, silent_video_path: Path, audio_wav_path: Path, output_path: Path, ffmpeg_path: str, fade_start: float,
) -> None:
    """無音映像＋音声を結合し、末尾 FADE_SECONDS 秒で映像・音声ともフェードアウトさせる。

    音声は 24kHz/モノラルの合成結果を 48kHz/ステレオの AAC へアップコンバートする
    （エンドカードの音声フォーマット要件）。
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    filter_complex = (
        f"[0:v]fade=t=out:st={fade_start:.3f}:d={FADE_SECONDS:.3f}[v];"
        f"[1:a]afade=t=out:st={fade_start:.3f}:d={FADE_SECONDS:.3f}[a]"
    )
    command = [
        ffmpeg_path, "-y",
        "-i", str(silent_video_path),
        "-i", str(audio_wav_path),
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg（結合・フェード）が失敗しました（終了コード{result.returncode}）:\n{result.stderr}")


# ============================================================
# メイン
# ============================================================


def main() -> int:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ffmpeg_path = resolve_ffmpeg_path(None)
    ffprobe_path = resolve_ffprobe_path(None, ffmpeg_path)

    bg_color = sample_background_color(ICON_PATH)
    print(f"背景色（アイコン外周の中央値）: {bg_color}")
    chip_color = _blend(bg_color, (255, 255, 255), 0.85)

    metan, zundamon = build_sprites()

    client = VoicevoxClient(speed_scale=SPEED_SCALE)
    print("VOICEVOX でナレーションを合成しています...")
    lines = synthesize_lines(client)
    for line in lines:
        print(f"  style={line.style_id} 尺={line.duration:.3f}s: {line.text}")

    timeline = build_timeline(lines)
    print(f"総尺（末尾ホールド込み）: {timeline.total_duration:.3f}s")
    if not (13.0 <= timeline.total_duration <= 16.0):
        print(
            f"警告: 総尺が目標レンジ(13-16秒)から外れています（{timeline.total_duration:.3f}s）",
            file=sys.stderr,
        )

    audio_wav_path = WORK_DIR / "full_audio.wav"
    with wave.open(str(audio_wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(timeline.sample_rate)
        wf.writeframes(timeline.pcm)

    headline_font = _load_font(round(HEIGHT * HEADLINE_FONT_RATIO))
    icon_label_font = _load_font(round(HEIGHT * ICON_LABEL_FONT_RATIO))
    icon_glyph_diameter = round(HEIGHT * ICON_CIRCLE_DIAMETER_RATIO)
    icon_glyph_font = _load_icon_font(round(icon_glyph_diameter * 0.55))

    icon_columns = build_icon_columns(
        icon_label_font,
        diameter=icon_glyph_diameter,
        gap_left=metan.final_x + metan.image.width,
        gap_right=zundamon.final_x,
    )

    frame_count = round(timeline.total_duration * FPS)
    frames = iter_frames(
        bg_color=bg_color,
        metan=metan,
        zundamon=zundamon,
        timeline=timeline,
        headline_font=headline_font,
        icon_label_font=icon_label_font,
        icon_glyph_font=icon_glyph_font,
        icon_columns=icon_columns,
        text_color=CHALK_COLOR,
        chip_color=chip_color,
    )

    silent_video_path = WORK_DIR / "silent_video.mp4"
    print(f"映像フレームを合成しています（{frame_count}フレーム）...")
    encode_silent_video(frames, frame_count=frame_count, output_path=silent_video_path, ffmpeg_path=ffmpeg_path)

    premux_path = WORK_DIR / "premux.mp4"
    fade_start = timeline.total_duration - FADE_SECONDS
    print("映像・音声を結合しています（末尾フェード込み）...")
    mux_video_and_audio(
        silent_video_path=silent_video_path,
        audio_wav_path=audio_wav_path,
        output_path=premux_path,
        ffmpeg_path=ffmpeg_path,
        fade_start=fade_start,
    )

    print("ラウドネス正規化（-14 LUFS）を適用しています...")
    try:
        mix_result = apply_bgm_and_loudnorm(premux_path, bgm_path=None, ffmpeg_path=ffmpeg_path, ffprobe_path=ffprobe_path)
    except AudioMixError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # build/ は D: へのジャンクションなので mix_result.output_path は実体が D: 側にある。
    # OUT_PATH（assets-kamishibai、C:側）とはドライブが異なり Path.replace（os.replace）が
    # 使えないため、shutil.move（ドライブをまたぐ場合はコピー+削除にフォールバックする）を使う。
    shutil.move(str(mix_result.output_path), str(OUT_PATH))

    print(f"完成: {OUT_PATH}")
    if mix_result.achieved_integrated is not None:
        print(f"ラウドネス正規化後: {mix_result.achieved_integrated:.1f} LUFS（目標 -14.0 LUFS）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
