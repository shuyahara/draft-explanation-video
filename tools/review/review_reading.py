"""レンダ済みナレーション音声を ASR（faster-whisper）で文字起こしし、台本（シーン YAML の
narration テキスト）と突き合わせて、漢字の誤読・読み飛ばし・不自然な区切りの候補を列挙する
ツール。

draft-explanation-video の台本執筆フローに「機械音声の読み上げ結果を検証する」ステップを
足す一環（2026-08-28）。review_script.py（台本レビュー）・review_video.py（映像レビュー）に
続く③読み上げレビュー。**台本・YAML の文言はこのツールでは一切編集しない**（差分候補の
列挙のみ）。差分の採否・分類（本当に誤読か／ASR側の誤認識か／表記揺れか）は人／Claude が
目視で行う。

## 方式（2026-08-28 改訂: かな比較）

1. シーンごとの TTS 済み wav（`scene_NN.wav`）を faster-whisper で単語単位のタイムスタンプ
   つき文字起こしする（1シーン1回。モデルのロードは全体で1回）。
2. `scene_NN.timing.json`（レンダ時にツールが書き出したセグメント別 start/end 秒）を使い、
   ASR の単語列をセグメント（YAML `narration[]` の各要素に対応）へ時刻で振り分ける。
3. セグメントごとに台本テキストと ASR テキストを**ひらがな化**して比較する
   （`pykakasi`）。台本側は YAML の `readings`（読み修正指定語）を先に適用してから
   ひらがな化する（＝指定読みで発音されているかどうかの検証を兼ねる）。数字は算用数字を
   漢数字表記に揃えてから `pykakasi` に渡し、「％」は「パーセント」に揃える。
   これにより「嗤う／笑う」「芥子／消し」のような**同音の別漢字**は一致扱いになり、
   本当に読みが違う箇所だけが残る。
4. かな一致率（`difflib.SequenceMatcher`）が閾値未満のセグメントだけを「要確認」として
   列挙する。漢字表記だけが違う（かなは一致する）箇所は、参考情報として末尾の別表に
   残す。
5. YAML の `readings` については、指定読み（カタカナ）をひらがな化したものが、該当
   セグメントの ASR ひらがな出力に含まれているかを別表に示す（発音そのものの検証）。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_reading.py ^
        --yaml scripts/20260827-cynicism/20260827-cynicism.yaml ^
        --audio-dir C:/Users/shuya/Projects/script-to-video/build/cynicism-audio-rev4 ^
        --model small

`--audio-dir`（セグメント別 wav + timing.json のディレクトリ）が最も精度が高い突き合わせ方式。
セグメント別音声が無い場合は `--mp4`（+ 同じディレクトリの `timeline.json`）でシーン単位の
粗い突き合わせにフォールバックする（セグメント別ではなくシーン全体のテキストを比較する）。

## 前提

- Python は script-to-video の venv を使う（Bash の `python` は Microsoft Store のスタブで
  動かない）。`PYTHONUTF8=1` を必ず付ける。
- `faster-whisper` と `pykakasi` が未インストールなら
  `uv pip install --python <venv>/Scripts/python.exe faster-whisper pykakasi` で追加する
  （script-to-video の主要依存ではないため pyproject.toml には加えない）。
- GPU なし（CPU・int8）を前提にモデル既定は `small`。より高精度が要る場合は `--model medium`
  （CPU で概ね実時間の0.5〜0.6倍程度で処理できる）。
- 初回実行時はモデルを Hugging Face Hub からダウンロードする（ネットワーク接続が必要）。
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pykakasi

STV_ROOT = Path(r"C:\Users\shuya\Projects\script-to-video")
sys.path.insert(0, str(STV_ROOT / "src"))

from script_to_video.loader import load_scene_yaml  # noqa: E402
from script_to_video.render import resolve_ffmpeg_path  # noqa: E402
from script_to_video.schema import Reading, Scene  # noqa: E402
from script_to_video.tts import SceneTiming, SegmentTiming  # noqa: E402

# ============================================================
# 定数
# ============================================================

DEFAULT_MODEL = "small"
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE_TYPE = "int8"
DEFAULT_THRESHOLD = 0.85
"""かな一致率の閾値。日本語は同音異字が多く、漢字表記レベルの一致では閾値0.9でもノイズが
多すぎたため（2026-08-28 実測で146/225件が要確認）、かな比較に切り替えたうえでの既定値。
必要に応じて --threshold で調整する。"""

BOUNDARY_TOLERANCE_S = 0.25
"""ASR単語の中心時刻がセグメント区間の外でも、この秒数以内なら区間内とみなす。"""

PUNCT_RE = re.compile(r"[、。！？「」『』・：／【】（）()\s,.!?\u3000]")

KANJI_RE = re.compile(r"[\u4e00-\u9fff]")

# 表記揺れの簡易正規化辞書（漢字表記レベルの参考差分でのみ使用。誤検出を減らすため、
# 台本側・ASR側の両方に適用してから比較する）。
VARIANT_NORMALIZATION: tuple[tuple[str, str], ...] = (
    ("分かる", "わかる"),
    ("出来る", "できる"),
    ("良い", "いい"),
    ("無い", "ない"),
    ("言う", "いう"),
    ("事", "こと"),
    ("物", "もの"),
    ("時", "とき"),
    ("為", "ため"),
    ("等", "など"),
    ("方", "ほう"),
    ("通り", "とおり"),
    ("全て", "すべて"),
    ("更に", "さらに"),
    ("又は", "または"),
    ("但し", "ただし"),
    ("尚", "なお"),
)

DIGIT_KANJI = ("〇", "一", "二", "三", "四", "五", "六", "七", "八", "九")
PLACE_KANJI = ("", "十", "百", "千")  # 1の位, 10の位, 100の位, 1000の位

NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


class ReviewReadingError(RuntimeError):
    """レビュー実行に失敗したときのエラー。"""


@dataclass
class SegmentResult:
    scene_id: int
    scene_title: str
    seg_index: int  # 1-based。シーン単位フォールバックでは 0。
    script_text: str
    asr_text: str
    kana_ratio: float
    kana_diff: str
    kanji_ratio: float
    kanji_diff: str


@dataclass
class ReadingRow:
    scene_id: int
    surface: str
    reading: str
    seg_index: int | None
    asr_text: str
    kana_ratio: float
    kana_matched: bool


# ============================================================
# YAML 読み込み
# ============================================================


def load_scenes(yaml_path: Path) -> list[Scene]:
    result = load_scene_yaml(yaml_path)
    if not result.ok or result.document is None:
        raise ReviewReadingError("YAML の読み込みに失敗しました:\n" + "\n".join(result.errors))
    return list(result.document.scenes)


# ============================================================
# timing.json / timeline.json 読み込み
# ============================================================


def load_scene_timing(audio_dir: Path, scene_id: int) -> SceneTiming | None:
    path = audio_dir / f"scene_{scene_id:02d}.timing.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return SceneTiming.from_dict(data)


def load_timeline_scene_spans(timeline_path: Path) -> dict[int, tuple[float, float]]:
    if not timeline_path.is_file():
        raise ReviewReadingError(f"timeline.json が見つかりません: {timeline_path}")
    data = json.loads(timeline_path.read_text(encoding="utf-8"))
    spans: dict[int, tuple[float, float]] = {}
    for entry in data.get("entries", []):
        if entry.get("kind") == "scene":
            spans[entry["scene_id"]] = (entry["start"], entry["end"])
    return spans


# ============================================================
# 数字の漢数字化（かな比較の前処理）
# ============================================================


def int_to_kanji(n: int) -> str:
    """0〜9999の整数を漢数字表記にする（千・百・十の前の「一」は省略する標準的な表記）。

    本ツールが扱う台本中の数値は1万未満のため、それ以上の桁は未対応（元の数字文字列を
    そのまま返す）。
    """

    if n == 0:
        return "〇"
    if n >= 10000:
        return str(n)
    digits = [int(c) for c in str(n)]
    length = len(digits)
    result = ""
    for i, d in enumerate(digits):
        place = PLACE_KANJI[length - 1 - i]
        if d == 0:
            continue
        if d == 1 and place:
            result += place
        else:
            result += DIGIT_KANJI[d] + place
    return result


def normalize_numbers(text: str) -> str:
    """算用数字を漢数字表記に寄せる（台本側の "1983" と ASR側の "千九百八十三" のような
    表記違いを、かな化する前に吸収する）。桁区切りのカンマは事前に除去する。小数点以下は
    桁ごとに読む（例: "39.6" → "三十九てん六"）。
    """

    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)

    def repl(m: re.Match[str]) -> str:
        raw = m.group(0)
        if "." in raw:
            int_part, _, frac_part = raw.partition(".")
            out = int_to_kanji(int(int_part)) if int_part else ""
            out += "てん" + "".join(DIGIT_KANJI[int(c)] for c in frac_part)
            return out
        return int_to_kanji(int(raw))

    return NUMBER_RE.sub(repl, text)


# ============================================================
# かな化・正規化・差分
# ============================================================

_KKS = pykakasi.kakasi()


def to_kana(text: str) -> str:
    """任意の日本語テキストをひらがな化する（pykakasi）。"""

    return "".join(item["hira"] for item in _KKS.convert(text))


def apply_readings(text: str, readings: list[Reading] | None) -> str:
    """YAML `readings` の指定（surface→カタカナ読み）をテキストへ適用する。"""

    if not readings:
        return text
    for r in readings:
        if r.surface in text:
            text = text.replace(r.surface, r.reading)
    return text


def kana_normalize(text: str, readings: list[Reading] | None = None) -> str:
    """かな比較用の正規化: (readings適用) → 数字の漢数字化 → ％→パーセント → かな化 → 記号除去。"""

    text = apply_readings(text, readings)
    text = normalize_numbers(text)
    text = text.replace("%", "パーセント")
    kana = to_kana(text)
    kana = PUNCT_RE.sub("", kana)
    return kana


def normalize_text(text: str) -> str:
    """漢字表記レベルの正規化（参考差分の算出用）。"""

    text = unicodedata.normalize("NFKC", text)
    text = PUNCT_RE.sub("", text)
    for kanji, kana in VARIANT_NORMALIZATION:
        text = text.replace(kanji, kana)
    return text


def summarize_diff(script_norm: str, asr_norm: str) -> str:
    """漢字表記レベルの差分の簡易分類（漢字置換／読み飛ばし疑い／ASR側のみの語）。"""

    sm = difflib.SequenceMatcher(None, script_norm, asr_norm)
    notes: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        script_part = script_norm[i1:i2]
        asr_part = asr_norm[j1:j2]
        if tag == "replace" and KANJI_RE.search(script_part) and KANJI_RE.search(asr_part):
            notes.append(f"漢字差替え「{script_part}」→「{asr_part}」")
        elif tag in ("delete", "replace") and len(script_part) >= 2:
            notes.append(f"読み飛ばし疑い「{script_part}」→「{asr_part}」" if asr_part else f"読み飛ばし疑い「{script_part}」")
        elif tag == "insert" and asr_part:
            notes.append(f"ASR側のみ「{asr_part}」")
        else:
            notes.append(f"{tag}:「{script_part}」→「{asr_part}」")
    return "; ".join(notes)


def summarize_kana_diff(script_kana: str, asr_kana: str) -> str:
    """かな比較レベルの差分の簡易分類（要確認テーブルに出す差分メモ）。"""

    sm = difflib.SequenceMatcher(None, script_kana, asr_kana)
    notes: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        script_part = script_kana[i1:i2]
        asr_part = asr_kana[j1:j2]
        if script_part and asr_part:
            notes.append(f"置換「{script_part}」→「{asr_part}」")
        elif script_part:
            notes.append(f"読み飛ばし疑い「{script_part}」")
        elif asr_part:
            notes.append(f"ASR側のみ「{asr_part}」")
    return "; ".join(notes)


def has_kanji_diff(diff: str) -> bool:
    return "漢字差替え" in diff


# ============================================================
# ASR（faster-whisper）
# ============================================================


def load_whisper_model(model_name: str, device: str, compute_type: str):
    from faster_whisper import WhisperModel  # 遅延importで起動を速くする

    return WhisperModel(model_name, device=device, compute_type=compute_type)


def transcribe_words(model, audio_path: Path) -> list[tuple[float, float, str]]:
    """音声ファイル全体を単語単位のタイムスタンプつきで文字起こしする。"""

    segments, _info = model.transcribe(
        str(audio_path), language="ja", word_timestamps=True, vad_filter=False
    )
    words: list[tuple[float, float, str]] = []
    for seg in segments:
        for w in seg.words or []:
            token = w.word.strip()
            if token:
                words.append((w.start, w.end, token))
    return words


def bucket_words_to_segments(
    words: list[tuple[float, float, str]], segments: list[SegmentTiming]
) -> list[str]:
    """ASR単語列を timing セグメントの時間窓へ割り当てる。

    窓内（±BOUNDARY_TOLERANCE_S）に入る単語はそのセグメントへ、外れる単語（無音区間の
    ASR側の空耳等）は最も近いセグメントへ寄せる。これにより ASR のタイムスタンプの
    微小なずれを吸収しつつ、単語を取りこぼさない。
    """

    bounds = [(s.start, s.end) for s in segments]
    buckets: list[list[str]] = [[] for _ in segments]
    for w_start, w_end, token in words:
        center = (w_start + w_end) / 2
        best_i, best_dist = None, None
        for i, (s, e) in enumerate(bounds):
            if s - BOUNDARY_TOLERANCE_S <= center <= e + BOUNDARY_TOLERANCE_S:
                dist = 0.0
            else:
                dist = min(abs(center - s), abs(center - e))
            if best_dist is None or dist < best_dist:
                best_dist, best_i = dist, i
        if best_i is not None:
            buckets[best_i].append(token)
    return ["".join(b) for b in buckets]


# ============================================================
# シーン単位の処理
# ============================================================


def build_reading_rows(
    scene: Scene,
    seg_texts: list[str],
    seg_asr_text: list[str],
    seg_asr_kana: list[str],
    seg_kana_ratio: list[float],
) -> list[ReadingRow]:
    rows: list[ReadingRow] = []
    if not scene.readings:
        return rows
    for r in scene.readings:
        target_kana = to_kana(r.reading)
        found = False
        for i, text in enumerate(seg_texts):
            if r.surface in text:
                found = True
                asr_kana = seg_asr_kana[i] if i < len(seg_asr_kana) else ""
                rows.append(
                    ReadingRow(
                        scene_id=scene.id,
                        surface=r.surface,
                        reading=r.reading,
                        seg_index=i + 1,
                        asr_text=seg_asr_text[i] if i < len(seg_asr_text) else "",
                        kana_ratio=seg_kana_ratio[i] if i < len(seg_kana_ratio) else 0.0,
                        kana_matched=target_kana in asr_kana,
                    )
                )
        if not found:
            rows.append(
                ReadingRow(
                    scene_id=scene.id,
                    surface=r.surface,
                    reading=r.reading,
                    seg_index=None,
                    asr_text="",
                    kana_ratio=0.0,
                    kana_matched=False,
                )
            )
    return rows


def _build_segment_result(
    scene: Scene, seg_index: int, script_text: str, asr_text: str
) -> tuple[SegmentResult, str]:
    """1区間ぶんの SegmentResult と、その区間の ASR かな文字列を返す。"""

    script_kana = kana_normalize(script_text, readings=scene.readings)
    asr_kana = kana_normalize(asr_text)
    kana_ratio = difflib.SequenceMatcher(None, script_kana, asr_kana).ratio() if script_kana else 1.0
    kana_diff = summarize_kana_diff(script_kana, asr_kana)

    kanji_script_norm = normalize_text(script_text)
    kanji_asr_norm = normalize_text(asr_text)
    kanji_ratio = (
        difflib.SequenceMatcher(None, kanji_script_norm, kanji_asr_norm).ratio()
        if kanji_script_norm
        else 1.0
    )
    kanji_diff = summarize_diff(kanji_script_norm, kanji_asr_norm)

    result = SegmentResult(
        scene_id=scene.id,
        scene_title=scene.title,
        seg_index=seg_index,
        script_text=script_text,
        asr_text=asr_text,
        kana_ratio=kana_ratio,
        kana_diff=kana_diff,
        kanji_ratio=kanji_ratio,
        kanji_diff=kanji_diff,
    )
    return result, asr_kana


def process_scene_audio_dir(
    model, scene: Scene, audio_dir: Path
) -> tuple[list[SegmentResult], list[ReadingRow], list[str]]:
    warnings: list[str] = []
    timing = load_scene_timing(audio_dir, scene.id)
    wav_path = audio_dir / f"scene_{scene.id:02d}.wav"
    if timing is None or not wav_path.is_file():
        warnings.append(f"シーン{scene.id}: 音声/timing json が見つかりません（{audio_dir}）")
        return [], [], warnings

    if len(timing.segments) != len(scene.narration):
        warnings.append(
            f"シーン{scene.id}: セグメント数不一致（YAML={len(scene.narration)} / "
            f"timing={len(timing.segments)}）。先頭から突き合わせ可能な件数のみ比較します"
        )

    words = transcribe_words(model, wav_path)
    seg_asr = bucket_words_to_segments(words, timing.segments)
    seg_texts = [seg.text for seg in scene.narration]

    n = min(len(seg_texts), len(seg_asr))
    results: list[SegmentResult] = []
    seg_asr_kana: list[str] = []
    for i in range(n):
        result, asr_kana = _build_segment_result(scene, i + 1, seg_texts[i], seg_asr[i])
        results.append(result)
        seg_asr_kana.append(asr_kana)

    kana_ratios = [r.kana_ratio for r in results]
    reading_rows = build_reading_rows(scene, seg_texts[:n], seg_asr[:n], seg_asr_kana, kana_ratios)
    return results, reading_rows, warnings


def process_scene_mp4(
    model,
    scene: Scene,
    mp4_path: Path,
    spans: dict[int, tuple[float, float]],
    ffmpeg_exe: str,
    tmp_dir: Path,
) -> tuple[list[SegmentResult], list[ReadingRow], list[str]]:
    warnings: list[str] = []
    span = spans.get(scene.id)
    if span is None:
        warnings.append(f"シーン{scene.id}: timeline.json にシーン区間が見つかりません")
        return [], [], warnings

    start, end = span
    clip_path = tmp_dir / f"scene_{scene.id:02d}.wav"
    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss",
        f"{start:.3f}",
        "-to",
        f"{end:.3f}",
        "-i",
        str(mp4_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(clip_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not clip_path.is_file():
        warnings.append(f"シーン{scene.id}: ffmpeg での音声抽出に失敗しました: {proc.stderr[-500:]}")
        return [], [], warnings

    segments, _info = model.transcribe(
        str(clip_path), language="ja", word_timestamps=False, vad_filter=False
    )
    asr_text = "".join(s.text.strip() for s in segments)
    script_text = "".join(seg.text for seg in scene.narration)

    result, asr_kana = _build_segment_result(scene, 0, script_text, asr_text)

    reading_rows = build_reading_rows(scene, [script_text], [asr_text], [asr_kana], [result.kana_ratio])
    return [result], reading_rows, warnings


# ============================================================
# Markdown 出力
# ============================================================


def escape_cell(text: str, limit: int = 120) -> str:
    text = text.replace("|", "\\|").replace("\n", " ")
    if len(text) > limit:
        text = text[:limit] + "…"
    return text


def build_output(
    *,
    yaml_path: Path,
    source_desc: str,
    granularity: str,
    model_name: str,
    device: str,
    compute_type: str,
    threshold: float,
    all_results: list[SegmentResult],
    reading_rows: list[ReadingRow],
    warnings: list[str],
    elapsed_s: float,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_scenes = len({r.scene_id for r in all_results})
    n_segments = len(all_results)
    flagged = [r for r in all_results if r.kana_ratio < threshold]
    flagged.sort(key=lambda r: r.kana_ratio)
    kanji_only = [
        r for r in all_results if r.kana_ratio >= threshold and has_kanji_diff(r.kanji_diff)
    ]
    kanji_only.sort(key=lambda r: r.kanji_ratio)

    lines: list[str] = []
    lines.append("# ASR による読み上げ検証（誤読・読み飛ばし候補）\n")
    lines.append(f"- 日時: {now}")
    lines.append(f"- 台本 YAML: {yaml_path}")
    lines.append(f"- 音声ソース: {source_desc}")
    lines.append(f"- 突き合わせ粒度: {granularity}")
    lines.append(f"- ASRモデル: faster-whisper {model_name}（device={device}, compute_type={compute_type}）")
    lines.append(f"- 比較方式: かな比較（台本側は YAML `readings` を適用後にひらがな化。数字は漢数字化、％はパーセント表記に統一してからひらがな化）")
    lines.append(f"- かな一致率の閾値: {threshold}")
    lines.append(f"- 対象: {n_scenes} シーン / {n_segments} 区間")
    lines.append(f"- 要確認（かな一致率が閾値未満）: {len(flagged)} 件")
    lines.append(f"- 参考: かなは一致するが漢字表記が異なる箇所: {len(kanji_only)} 件")
    lines.append(f"- ASR処理時間: {elapsed_s:.0f}秒")
    lines.append("")
    lines.append(
        "> 本ツールは差分候補を列挙するだけで、誤読かどうかの判定は行わない。"
        "台本側・ASR側ともにひらがな化して比較するため、「嗤う／笑う」「芥子／消し」のような"
        "**同音の別漢字**は一致扱いになる（要確認からは外れ、末尾の参考表に回る）。"
        "一方で、ASRのひらがな化自体の精度（`pykakasi`の辞書の癖）や助詞の聞き取り違い、"
        "セグメント境界のタイムスタンプずれも混ざるため、要確認に残った箇所も人が目視で"
        "分類すること。台本・YAMLはこのツールでは編集しない。\n"
    )

    lines.append("## 要確認（かな一致率が閾値未満）\n")
    if flagged:
        lines.append("| シーン | 区間 | 台本 | ASR | かな一致率 | 差分（かな） |")
        lines.append("|---|---|---|---|---|---|")
        for r in flagged:
            seg_label = f"#{r.seg_index}" if r.seg_index else "(シーン全体)"
            lines.append(
                f"| {r.scene_id}: {escape_cell(r.scene_title, 24)} | {seg_label} | "
                f"{escape_cell(r.script_text)} | {escape_cell(r.asr_text)} | "
                f"{r.kana_ratio:.2f} | {escape_cell(r.kana_diff, 200)} |"
            )
    else:
        lines.append("該当なし。")
    lines.append("")

    lines.append("## 読み修正（YAML `readings`）の ASR 上の再現状況\n")
    if reading_rows:
        lines.append("| シーン | 表記 | 指定読み | 区間 | ASR出力 | かな一致率 | 指定読みがASRのかな出力に含まれるか |")
        lines.append("|---|---|---|---|---|---|---|")
        for row in reading_rows:
            seg_label = f"#{row.seg_index}" if row.seg_index else "(未検出)"
            mark = "○" if row.kana_matched else "×"
            lines.append(
                f"| {row.scene_id} | {row.surface} | {row.reading} | {seg_label} | "
                f"{escape_cell(row.asr_text)} | {row.kana_ratio:.2f} | {mark} |"
            )
        lines.append("")
        lines.append(
            "> 「指定読みがASRのかな出力に含まれるか」は、指定読み（カタカナ）をひらがな化した"
            "文字列が、該当セグメントのASR出力をひらがな化した文字列に部分文字列として含まれるかの"
            "判定。○であれば指定通りに発音されている強い根拠になる。×の場合でも、区間の"
            "「かな一致率」が閾値以上であれば実質的に問題なし（語順の違いや軽微なASR誤認識で"
            "部分一致が崩れただけの可能性が高い）。かな一致率が低い×だけが要確認の対象。\n"
        )
    else:
        lines.append("YAML に `readings` の指定なし。\n")

    lines.append("## 参考: かなは一致するが漢字表記が異なる箇所（対応不要）\n")
    lines.append(
        "ASRが同音の別漢字を選んだだけで、発音（かな一致率）は閾値以上の箇所。"
        "台本の誤読ではなくASR側の表記選択の違いなので、基本的に対応不要。\n"
    )
    if kanji_only:
        lines.append("| シーン | 区間 | 台本 | ASR | かな一致率 | 漢字一致率 | 漢字差分 |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in kanji_only:
            seg_label = f"#{r.seg_index}" if r.seg_index else "(シーン全体)"
            lines.append(
                f"| {r.scene_id}: {escape_cell(r.scene_title, 24)} | {seg_label} | "
                f"{escape_cell(r.script_text)} | {escape_cell(r.asr_text)} | "
                f"{r.kana_ratio:.2f} | {r.kanji_ratio:.2f} | {escape_cell(r.kanji_diff, 200)} |"
            )
    else:
        lines.append("該当なし。")
    lines.append("")

    lines.append("## 全区間一覧（付録・シーン順）\n")
    lines.append("| シーン | 区間 | 台本 | ASR | かな一致率 | 漢字一致率 |")
    lines.append("|---|---|---|---|---|---|")
    for r in sorted(all_results, key=lambda r: (r.scene_id, r.seg_index)):
        seg_label = f"#{r.seg_index}" if r.seg_index else "(シーン全体)"
        lines.append(
            f"| {r.scene_id}: {escape_cell(r.scene_title, 24)} | {seg_label} | "
            f"{escape_cell(r.script_text)} | {escape_cell(r.asr_text)} | "
            f"{r.kana_ratio:.2f} | {r.kanji_ratio:.2f} |"
        )
    lines.append("")

    if warnings:
        lines.append("## 警告\n")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines) + "\n"


# ============================================================
# CLI
# ============================================================


def default_out_path(yaml_path: Path, references_dir: Path) -> Path:
    folder_name = yaml_path.parent.name
    topic = re.sub(r"^\d{8}-", "", folder_name)
    today = datetime.now().strftime("%Y%m%d")
    return references_dir / f"{today}-{topic}-reading-check.md"


def parse_scene_filter(raw: str | None) -> set[int] | None:
    if not raw:
        return None
    return {int(x) for x in raw.split(",") if x.strip()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="レンダ済みナレーション音声をASRで文字起こしし、台本テキストとかな比較して誤読候補を列挙する"
    )
    parser.add_argument("--yaml", required=True, help="シーン YAML のパス")
    parser.add_argument("--audio-dir", default=None, help="scene_NN.wav + scene_NN.timing.json のディレクトリ（最も精度が高い方式）")
    parser.add_argument("--mp4", default=None, help="--audio-dir が無い場合のフォールバック: レンダ済みMP4（シーン単位の粗い突き合わせ）")
    parser.add_argument("--timeline", default=None, help="--mp4 使用時の timeline.json パス（既定: mp4と同じディレクトリ）")
    parser.add_argument("--out", default=None, help="出力先パス（既定: references/{実行日}-{台本フォルダ名（先頭の日付は除去）}-reading-check.md）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"faster-whisperのモデル名（既定: {DEFAULT_MODEL}。例: small, medium）")
    parser.add_argument("--device", default=DEFAULT_DEVICE, help=f"既定: {DEFAULT_DEVICE}")
    parser.add_argument("--compute-type", default=DEFAULT_COMPUTE_TYPE, help=f"既定: {DEFAULT_COMPUTE_TYPE}")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help=f"かな一致率の閾値（既定 {DEFAULT_THRESHOLD}）")
    parser.add_argument("--scenes", default=None, help="カンマ区切りのシーン番号フィルタ（既定: 全シーン）")
    parser.add_argument("--ffmpeg-path", default=None, help="ffmpeg実行ファイルのパス（--mp4使用時、既定: 自動検出）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    yaml_path = Path(args.yaml)
    if not yaml_path.is_file():
        print(f"YAMLファイルが見つかりません: {yaml_path}", file=sys.stderr)
        return 1

    if not args.audio_dir and not args.mp4:
        print("--audio-dir か --mp4 のいずれかを指定してください", file=sys.stderr)
        return 1

    try:
        scenes = load_scenes(yaml_path)
    except ReviewReadingError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    scene_filter = parse_scene_filter(args.scenes)
    if scene_filter:
        scenes = [s for s in scenes if s.id in scene_filter]
    if not scenes:
        print("対象シーンがありません", file=sys.stderr)
        return 2

    print(f"モデルをロードします: {args.model}（device={args.device}, compute_type={args.compute_type}）")
    t_load0 = time.time()
    try:
        model = load_whisper_model(args.model, args.device, args.compute_type)
    except ImportError as exc:
        print(f"faster-whisper が見つかりません。インストールしてください: {exc}", file=sys.stderr)
        return 1
    print(f"モデルロード完了（{time.time() - t_load0:.0f}秒）")

    all_results: list[SegmentResult] = []
    reading_rows: list[ReadingRow] = []
    warnings: list[str] = []

    t0 = time.time()

    if args.audio_dir:
        audio_dir = Path(args.audio_dir)
        source_desc = f"{audio_dir}（セグメント別 wav + timing.json）"
        granularity = "セグメント単位（narration[] の各要素）"
        for scene in scenes:
            print(f"シーン{scene.id}「{scene.title}」を処理中…")
            results, rows, warns = process_scene_audio_dir(model, scene, audio_dir)
            all_results.extend(results)
            reading_rows.extend(rows)
            warnings.extend(warns)
    else:
        mp4_path = Path(args.mp4)
        timeline_path = Path(args.timeline) if args.timeline else mp4_path.parent / "timeline.json"
        spans = load_timeline_scene_spans(timeline_path)
        ffmpeg_exe = resolve_ffmpeg_path(args.ffmpeg_path)
        source_desc = f"{mp4_path}（timeline.json: {timeline_path}）"
        granularity = "シーン単位（narration[] 全体を連結して比較。--audio-dir よりも粗い）"
        with tempfile.TemporaryDirectory(prefix="review_reading_") as tmp:
            tmp_dir = Path(tmp)
            for scene in scenes:
                print(f"シーン{scene.id}「{scene.title}」を処理中…")
                results, rows, warns = process_scene_mp4(model, scene, mp4_path, spans, ffmpeg_exe, tmp_dir)
                all_results.extend(results)
                reading_rows.extend(rows)
                warnings.extend(warns)

    elapsed = time.time() - t0
    print(f"ASR処理完了（{elapsed:.0f}秒、{len(all_results)}区間）")

    references_dir = Path(__file__).resolve().parents[2] / "references"
    out_path = Path(args.out) if args.out else default_out_path(yaml_path, references_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    output = build_output(
        yaml_path=yaml_path,
        source_desc=source_desc,
        granularity=granularity,
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
        threshold=args.threshold,
        all_results=all_results,
        reading_rows=reading_rows,
        warnings=warnings,
        elapsed_s=elapsed,
    )
    out_path.write_text(output, encoding="utf-8")

    n_flagged = sum(1 for r in all_results if r.kana_ratio < args.threshold)
    print(f"保存しました: {out_path}（要確認 {n_flagged}/{len(all_results)} 件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
