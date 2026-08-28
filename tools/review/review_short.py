"""レンダ済みショート動画（TTS専用YAML + 完成mp4）を、ナレーションセグメント単位の静止画で
別モデル（GPT。Codex CLI 経由）にレビューさせるツール。

review_video.py（本編用）のショート版（2026-08-28 追加）。ショートは beats[] を持たない
TTS専用の最小 YAML（narration[] のみ）で作られるため、シーン・ビート単位ではなく
narration[] の各セグメントを単位にする。scene_id は常に1、beat_num はセグメント番号
（1始まり）として BeatRecord を組み立て、review_video.py の BeatRecord / build_gpt_prompt /
run_gpt_review（GPT_SCOPE_RULES込み）をそのまま再利用する。

決定論チェック（テロップの捏造検出など）はショートには telop が無いため行わない。
GPT観点には字幕の物理崩れ（はみ出し・重なり・行数過多）の確認を含める（review_video.py の
観点⑤と同じ）。

**台本・YAML・動画はこのツールでは一切編集しない**（指摘の生成のみ）。採否判断と反映は
人／Claude が行う。

## 使い方

    "C:\\Users\\shuya\\Projects\\script-to-video\\.venv\\Scripts\\python.exe" ^
        tools/review/review_short.py ^
        --yaml C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/short-tts.yaml ^
        --mp4 C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/short.mp4 ^
        --timings-dir C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/audio ^
        --out C:/Users/shuya/Projects/script-to-video/build/cynicism-short1/review/video-review.md

`--skip-gpt` を付けると静止画抽出だけ行う（GPT 呼び出しなし）。

## 前提

review_video.py と同じ（script-to-video の venv python で実行、ffmpeg、Codex CLI ログイン済み）。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

STV_ROOT = Path(r"C:\Users\shuya\Projects\script-to-video")
sys.path.insert(0, str(STV_ROOT / "src"))

from script_to_video.loader import load_scene_yaml  # noqa: E402
from script_to_video.render import resolve_ffmpeg_path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_video import (  # noqa: E402
    BeatRecord,
    DEFAULT_PER_CALL,
    DEFAULT_TIMEOUT_S,
    ReviewVideoError,
    extract_still,
    resolve_codex_exe,
    run_gpt_review,
)

STILL_WIDTH = 960


@dataclass
class NarrationSegment:
    index: int  # 1始まり
    text: str
    start: float
    end: float
    pause_after: float


def load_narration_segments(yaml_path: Path) -> list[NarrationSegment]:
    result = load_scene_yaml(yaml_path)
    if not result.ok or result.document is None:
        msgs = "\n".join(f"  - {e}" for e in result.errors)
        raise ReviewVideoError(f"YAML の読み込みに失敗しました:\n{msgs}")
    scene = result.document.scenes[0]
    timing_path = None
    segments: list[NarrationSegment] = []
    for i, seg in enumerate(scene.narration, start=1):
        segments.append(
            NarrationSegment(index=i, text=seg.text, start=0.0, end=0.0, pause_after=seg.pause_after)
        )
    return segments


def load_timing_segments(timings_dir: Path, scene_id: int = 1) -> list[dict]:
    path = timings_dir / f"scene_{scene_id:02d}.timing.json"
    if not path.is_file():
        raise ReviewVideoError(f"timing json が見つかりません: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["segments"]


def build_beat_records(yaml_path: Path, timings_dir: Path) -> list[BeatRecord]:
    narration_segments = load_narration_segments(yaml_path)
    timing_segments = load_timing_segments(timings_dir)
    if len(narration_segments) != len(timing_segments):
        raise ReviewVideoError(
            f"narration[] の件数（{len(narration_segments)}）と timing.json の segments 件数"
            f"（{len(timing_segments)}）が一致しません"
        )
    records: list[BeatRecord] = []
    for seg, timing in zip(narration_segments, timing_segments):
        start = float(timing["start"])
        end = float(timing["end"])
        mid = (start + end) / 2
        records.append(
            BeatRecord(
                scene_id=1,
                beat_num=seg.index,
                beat_type="image",
                start=start,
                end=end,
                abs_time=mid,
                narration=seg.text,
                telop=None,
                chapter_title=None,
                visual_intent=None,
                gen_prompt=None,
                cut_reason=f"ナレーションセグメント{seg.index}の中間時刻",
            )
        )
    return records


def build_markdown(
    *,
    yaml_path: Path,
    mp4_path: Path,
    gpt_responses: list[str],
    gpt_failures: list[str],
    skipped_gpt: bool,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [
        "# GPT（Codex CLI 経由）によるショート映像レビュー\n",
        f"- 日時: {now}",
        f"- YAML: {yaml_path}",
        f"- MP4: {mp4_path}",
        "",
        "決定論チェックはショートには telop が無いため実施しない。GPT観点は review_video.py と同じ7点"
        "（うち⑤字幕・テロップの物理的な崩れは細かくても報告対象、GPT_SCOPE_RULES準拠）。",
        "",
        "## GPT 画像レビュー\n",
    ]
    if skipped_gpt:
        parts.append("`--skip-gpt` のため未実行。")
    elif not gpt_responses and not gpt_failures:
        parts.append("対象セグメントがありませんでした。")
    else:
        for response in gpt_responses:
            parts.append(response)
            parts.append("")
        if gpt_failures:
            parts.append("### 未レビュー\n")
            for msg in gpt_failures:
                parts.append(f"- {msg}")
            parts.append("")
    return "\n".join(parts) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="レンダ済みショート動画をナレーションセグメント単位でGPTレビューする")
    parser.add_argument("--yaml", required=True, help="TTS専用シーン YAML のパス")
    parser.add_argument("--mp4", required=True, help="完成 MP4 のパス")
    parser.add_argument("--timings-dir", required=True, help="scene_01.timing.json の場所")
    parser.add_argument("--out", required=True, help="出力 Markdown のパス")
    parser.add_argument("--per-call", type=int, default=DEFAULT_PER_CALL, help=f"1回のcodex呼び出しに載せる画像数（既定 {DEFAULT_PER_CALL}）")
    parser.add_argument("--skip-gpt", action="store_true", help="静止画抽出だけ行い、GPTレビューは呼ばない")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, help=f"codex exec 1回あたりのタイムアウト秒（既定 {DEFAULT_TIMEOUT_S:.0f}）")
    parser.add_argument("--ffmpeg-path", default=None, help="ffmpeg 実行ファイルのパス（既定: 自動検出）")
    parser.add_argument("--codex-path", default=None, help="codex 実行ファイルのパス（既定: 自動検出）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    yaml_path = Path(args.yaml)
    mp4_path = Path(args.mp4)
    timings_dir = Path(args.timings_dir)
    out_path = Path(args.out)

    try:
        ffmpeg_exe = resolve_ffmpeg_path(args.ffmpeg_path)
        records = build_beat_records(yaml_path, timings_dir)
    except ReviewVideoError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    stills_dir = out_path.parent / "stills"
    for r in records:
        still_path = stills_dir / f"seg{r.beat_num:02d}.jpg"
        try:
            extract_still(ffmpeg_exe, mp4_path, r.abs_time, still_path)
            r.still_path = still_path
        except ReviewVideoError as exc:
            r.still_error = str(exc)

    total_stills = sum(1 for r in records if r.still_path)
    print(f"静止画抽出: {total_stills}/{len(records)} 枚（{stills_dir}）")

    gpt_responses: list[str] = []
    gpt_failures: list[str] = []
    if not args.skip_gpt:
        try:
            codex_exe = resolve_codex_exe(args.codex_path)
        except ReviewVideoError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        start_time = time.time()
        gpt_responses, gpt_failures = run_gpt_review(
            records, codex_exe=codex_exe, per_call=args.per_call, timeout=args.timeout
        )
        print(f"GPT画像レビュー所要: {time.time() - start_time:.0f}秒")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        build_markdown(
            yaml_path=yaml_path,
            mp4_path=mp4_path,
            gpt_responses=gpt_responses,
            gpt_failures=gpt_failures,
            skipped_gpt=args.skip_gpt,
        ),
        encoding="utf-8",
    )
    print(f"保存しました: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
